"""
AI Nutrition Agent
Implements Tool Calling architecture connecting conversational intent
to deterministic backend engines:
- Nutrition Calculator
- Food Database
- Meal Planner
- Food Logger
- Progress Analyzer
- Substitution Engine
- Safety Layer
- RAG Retriever
Supports both external LLM tool calling (OpenAI/compatible) and built-in deterministic agent orchestration.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.profile import Profile
from app.models.chat import ChatSession, ChatMessage
from app.services.safety_service import SafetyService
from app.services.nutrition_calculator import NutritionCalculator
from app.services.food_service import FoodService
from app.services.food_logger import FoodLogger
from app.services.meal_planner import MealPlanner
from app.services.substitution_engine import SubstitutionEngine
from app.services.progress_analyzer import ProgressAnalyzer
from app.services.rag_service import RAGRetriever

SYSTEM_PROMPT = """You are a personal nutrition assistant.
Your job is to help the user plan meals, understand nutrition, track food intake, and interpret progress.
Always use the nutrition calculation tools for numerical calculations.
Never invent nutritional values when a food database lookup is available.
Clearly distinguish estimated values from exact database values.
Respect the user's dietary preferences, allergies, budget, schedule, and goal.
Do not diagnose medical conditions.
Do not prescribe treatment or medication.
For potentially serious medical or eating-related concerns, recommend consulting an appropriately qualified healthcare professional.
When information is missing and materially affects the recommendation, ask for it.
Use the user's historical nutrition and weight data when making progress recommendations.
Do not make drastic changes based on a single day's data.
Be practical and culturally appropriate, including Indian foods when relevant."""


# Tool Definitions for LLM function calling
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Retrieves the current user's profile, demographics, goals, dietary restrictions, and target calories/macros.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_nutrition_targets",
            "description": "Calculates deterministic BMR, TDEE, calories, and macronutrient targets based on weight, height, age, sex, activity, and goal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Current body weight in kg"},
                    "height_cm": {"type": "number", "description": "Height in cm"},
                    "age": {"type": "integer", "description": "Age in years"},
                    "sex": {"type": "string", "enum": ["male", "female", "other"]},
                    "activity_level": {"type": "string", "enum": ["sedentary", "light", "moderate", "very_active", "athlete"]},
                    "goal": {"type": "string", "enum": ["weight_loss", "weight_maintenance", "weight_gain", "muscle_gain", "general_health"]},
                    "custom_deficit": {"type": "number", "description": "Optional calorie deficit in kcal"},
                    "custom_surplus": {"type": "number", "description": "Optional calorie surplus in kcal"}
                },
                "required": ["weight_kg", "height_cm", "age", "sex", "activity_level", "goal"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_food",
            "description": "Searches the food database for verified nutritional content, calories, and serving sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Food name e.g. 'roti', 'dal', 'paneer'"},
                    "category": {"type": "string", "description": "Optional food category"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_food",
            "description": "Logs foods from natural language text into today's meal records and updates daily totals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Sentence describing what was eaten, e.g., 'I ate 2 eggs and 1 glass of milk'"},
                    "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "evening_snack", "snack"]}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_food_log",
            "description": "Retrieves today's logged meals, consumed calories, protein, carbs, fat, fiber, water, and remaining targets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format (defaults to today)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_meal_plan",
            "description": "Generates a full day's customized meal plan mapped to calorie and macro targets with cooking directions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_date": {"type": "string", "description": "Date for the meal plan (YYYY-MM-DD)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_food_substitution",
            "description": "Finds nutritionally reasonable substitutes for a food while respecting diet type and matching calories/macros.",
            "parameters": {
                "type": "object",
                "properties": {
                    "food_name": {"type": "string", "description": "Food to be substituted, e.g., 'paneer' or 'banana'"}
                },
                "required": ["food_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_weight",
            "description": "Logs a new body weight measurement in kilograms with optional note.",
            "parameters": {
                "type": "object",
                "properties": {
                    "weight_kg": {"type": "number", "description": "Scale weight in kilograms"},
                    "note": {"type": "string", "description": "Optional note"}
                },
                "required": ["weight_kg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weight_history",
            "description": "Retrieves historical weight records and 7-day rolling averages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days of history"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_progress",
            "description": "Analyzes weekly adherence, calorie and protein trends, scale weight trajectory, and generates adaptive recommendations.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_nutrition_evidence",
            "description": "Retrieves scientific citations and evidence from ICMR-NIN, WHO, ISSN, USDA, and Harvard for questions like 'What is protein?' or 'What foods contain iron?'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nutrition concept or research question"}
                },
                "required": ["query"]
            }
        }
    }
]


class NutritionAgent:

    @classmethod
    def execute_tool(
        cls,
        db: Session,
        user_id: int,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes a deterministic tool against backend database and services.
        """
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if tool_name == "get_user_profile":
            if not profile:
                return {"error": "Profile not configured yet."}
            return {
                "name": profile.name,
                "age": profile.age,
                "sex": profile.sex,
                "current_weight_kg": profile.current_weight_kg,
                "target_weight_kg": profile.target_weight_kg,
                "goal": profile.goal,
                "diet_type": profile.diet_type,
                "bmr": profile.bmr,
                "tdee": profile.tdee,
                "target_calories": profile.target_calories,
                "target_protein_g": profile.target_protein_g,
                "target_carbs_g": profile.target_carbs_g,
                "target_fat_g": profile.target_fat_g,
                "target_water_ml": profile.target_water_ml,
            }

        elif tool_name == "calculate_nutrition_targets":
            calc = NutritionCalculator.calculate_all(
                weight_kg=arguments["weight_kg"],
                height_cm=arguments["height_cm"],
                age=arguments["age"],
                sex=arguments["sex"],
                activity_level=arguments["activity_level"],
                goal=arguments["goal"],
                custom_deficit=arguments.get("custom_deficit"),
                custom_surplus=arguments.get("custom_surplus")
            )
            return calc

        elif tool_name == "search_food":
            foods = FoodService.search_foods(
                db=db,
                query=arguments.get("query", ""),
                category=arguments.get("category"),
                limit=5
            )
            return {
                "results": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "serving_size": f.serving_size,
                        "calories": f.calories,
                        "protein_g": f.protein_g,
                        "carbs_g": f.carbs_g,
                        "fat_g": f.fat_g,
                        "fiber_g": f.fiber_g
                    }
                    for f in foods
                ]
            }

        elif tool_name == "log_food":
            text = arguments["text"]
            date_str = arguments.get("date") or datetime.now().strftime("%Y-%m-%d")
            result = FoodLogger.log_meal_from_text(db, user_id, text, date_str)
            return result

        elif tool_name == "get_daily_food_log":
            date_str = arguments.get("date") or datetime.now().strftime("%Y-%m-%d")
            summary = ProgressAnalyzer.get_dashboard_summary(db, user_id, date_str)
            return summary

        elif tool_name == "generate_meal_plan":
            if not profile:
                return {"error": "Please set up your profile first to generate a meal plan."}
            plan_date = arguments.get("plan_date") or datetime.now().strftime("%Y-%m-%d")
            plan = MealPlanner.generate_daily_plan(db, profile, plan_date)
            return plan

        elif tool_name == "suggest_food_substitution":
            food_name = arguments["food_name"]
            diet_type = profile.diet_type if profile else "vegetarian"
            allergies = profile.allergies if profile else ""
            subs = SubstitutionEngine.suggest_substitution(
                db=db,
                food_name=food_name,
                diet_type=diet_type,
                allergies=allergies
            )
            return subs

        elif tool_name == "log_weight":
            wt = float(arguments["weight_kg"])
            note = arguments.get("note")
            res = ProgressAnalyzer.log_weight(db, user_id, wt, note=note)
            return res

        elif tool_name == "get_weight_history":
            days = arguments.get("days", 30)
            history = ProgressAnalyzer.get_weight_history(db, user_id, days)
            return {"history": history}

        elif tool_name == "analyze_progress":
            prog = ProgressAnalyzer.analyze_weekly_progress(db, user_id)
            return prog

        elif tool_name == "retrieve_nutrition_evidence":
            query = arguments["query"]
            evidence = RAGRetriever.retrieve_evidence(db, query)
            return evidence

        return {"error": f"Tool '{tool_name}' not recognized."}

    @classmethod
    async def chat(
        cls,
        db: Session,
        user_id: int,
        session_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Primary entry point for chatting with the AI Nutrition Agent.
        Executes safety screening, manages context, triggers tool calling,
        and saves conversational memory.
        """
        # 1. Safety Screening
        safety_check = SafetyService.check_input_safety(user_message)
        if not safety_check["is_safe_for_automated_planning"]:
            # Red flag clinical or eating disorder trigger detected
            disclaimer_msg = (
                f"{safety_check['disclaimer']}\n\n"
                "Please consult a physician, registered dietitian, or mental healthcare specialist."
            )
            # Store message
            db.add(ChatMessage(session_id=session_id, role="user", content=user_message))
            db.add(ChatMessage(
                session_id=session_id,
                role="assistant",
                content=disclaimer_msg,
                tool_calls=json.dumps([{"safety_trigger": safety_check["flagged_categories"]}])
            ))
            db.commit()

            return {
                "role": "assistant",
                "content": disclaimer_msg,
                "tool_calls_executed": [{"name": "safety_screener", "arguments": {"flagged": safety_check["flagged_categories"]}}],
                "safety_disclaimer": safety_check["disclaimer"]
            }

        # Save user message
        db.add(ChatMessage(session_id=session_id, role="user", content=user_message))
        db.commit()

        # Check if live LLM API is available
        if settings.LLM_API_KEY and not settings.LLM_API_KEY.startswith("test_"):
            try:
                response = await cls._chat_with_external_llm(db, user_id, session_id, user_message)
                return response
            except Exception as e:
                # Graceful fallback to deterministic local orchestrator
                pass

        # Built-in deterministic agent tool caller
        response = cls._chat_with_local_orchestrator(db, user_id, session_id, user_message)
        return response

    @classmethod
    def _chat_with_local_orchestrator(
        cls,
        db: Session,
        user_id: int,
        session_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Intelligent local semantic agent that interprets requests,
        dispatches to backend tools, and formulates clear, personalized responses.
        """
        msg_lower = user_message.lower().strip()
        executed_tools = []
        assistant_reply = ""

        # 1. Intent: Food Logging ("I ate...", "Logged 2 eggs", "Had lunch...")
        if re.search(r'\b(ate|had|having|eaten|log food|logged|drank)\b', msg_lower) and not re.search(r'\b(what should i eat|give me|plan|suggest)\b', msg_lower):
            tool_args = {"text": user_message}
            log_result = cls.execute_tool(db, user_id, "log_food", tool_args)
            executed_tools.append({"name": "log_food", "args": tool_args, "result": log_result})

            if log_result.get("success"):
                nutr = log_result["total_nutrition"]
                items_str = ", ".join(f"{it['quantity']} {it['unit']} {it['food_name']}" for it in log_result["items"])
                assistant_reply = (
                    f"✅ **Meal Logged Successfully!**\n\n"
                    f"**Logged Items:** {items_str}\n\n"
                    f"**Nutritional Breakdown:**\n"
                    f"- **Calories:** {nutr['calories']} kcal\n"
                    f"- **Protein:** {nutr['protein_g']} g\n"
                    f"- **Carbohydrates:** {nutr['carbs_g']} g\n"
                    f"- **Fat:** {nutr['fat_g']} g\n"
                    f"- **Fiber:** {nutr['fiber_g']} g\n\n"
                )
                if log_result.get("clarifications_needed"):
                    assistant_reply += f"ℹ️ *Note:* {log_result['clarifications_needed'][0]}\n"
                assistant_reply += "Your daily dashboard has been updated."
            else:
                assistant_reply = log_result.get("message", "Could not parse food items.")

        # 2. Intent: Meal Plan Generation ("meal plan", "what should i eat for breakfast", "high protein dinner")
        elif re.search(r'\b(meal plan|plan my meals|what should i eat|diet plan|breakfast options|dinner options)\b', msg_lower):
            plan_result = cls.execute_tool(db, user_id, "generate_meal_plan", {})
            executed_tools.append({"name": "generate_meal_plan", "args": {}, "result": plan_result})

            if "meals" in plan_result:
                meals = plan_result["meals"]
                assistant_reply = (
                    f"📋 **Personalized Meal Plan Generated**\n\n"
                    f"Target: **{int(plan_result['targets']['target_calories'])} kcal** | "
                    f"Protein: **{int(plan_result['targets']['target_protein_g'])}g**\n\n"
                )
                for slot, m in meals.items():
                    items_txt = ", ".join(f"{it['food_name']} ({it['serving_description']})" for it in m["items"])
                    assistant_reply += (
                        f"### {m['slot_name']}: {m['meal_name']}\n"
                        f"- **Foods:** {items_txt}\n"
                        f"- **Nutrition:** {m['total_calories']} kcal | {m['total_protein_g']}g Protein | {m['total_carbs_g']}g Carbs\n"
                        f"- **Prep:** {m['preparation_instructions']}\n\n"
                    )
                assistant_reply += "You can view and customize this plan anytime in your **Meal Plan** tab!"
            else:
                assistant_reply = plan_result.get("error", "Please configure your profile first.")

        # 3. Intent: Food Substitution ("replace paneer", "don't have bananas", "substitute chicken")
        elif re.search(r'\b(replace|substitute|don\'t have|instead of|alternative to)\b', msg_lower):
            # Extract food name
            match = re.search(r'(replace|substitute|alternative to|instead of)\s+([a-zA-Z\s]+?)(?:\s+with|\s+for|\s+today|\?|$)', msg_lower)
            food_to_replace = match.group(2).strip() if match else "paneer"
            sub_args = {"food_name": food_to_replace}
            sub_res = cls.execute_tool(db, user_id, "suggest_food_substitution", sub_args)
            executed_tools.append({"name": "suggest_food_substitution", "args": sub_args, "result": sub_res})

            subs = sub_res.get("substitutes", [])
            if subs:
                assistant_reply = (
                    f"🔄 **Nutritional Substitutions for {food_to_replace.title()}**\n\n"
                    f"Targeting ~{int(sub_res.get('target_calories', 200))} kcal and {int(sub_res.get('target_protein_g', 10))}g protein:\n\n"
                )
                for s in subs:
                    assistant_reply += (
                        f"- **{s['substitute_food']}**: {s['serving_description']}\n"
                        f"  *Nutrition:* {s['nutrition']['calories']} kcal | {s['nutrition']['protein_g']}g Protein\n"
                        f"  *{s['fit_note']}*\n\n"
                    )
            else:
                assistant_reply = f"Could not find exact substitutions for '{food_to_replace}'. Try paneer, tofu, eggs, or lentils."

        # 4. Intent: Weight Logging ("weight is 74", "log weight 68 kg", "weighed 70")
        elif re.search(r'\b(weight is|weighed|log weight|weight:?)\s*(\d+(?:\.\d+)?)\b', msg_lower) or re.search(r'(\d+(?:\.\d+)?)\s*(kg|kilos|kilograms)', msg_lower):
            wt_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilos|kilograms)?', msg_lower)
            wt_val = float(wt_match.group(1)) if wt_match else 70.0
            wt_args = {"weight_kg": wt_val}
            wt_res = cls.execute_tool(db, user_id, "log_weight", wt_args)
            executed_tools.append({"name": "log_weight", "args": wt_args, "result": wt_res})

            assistant_reply = (
                f"⚖️ **Weight Logged: {wt_val} kg**\n\n"
                f"7-Day Rolling Average: **{wt_res.get('rolling_avg_7d')} kg**\n\n"
                "Remember that day-to-day body weight fluctuates naturally due to water balance, sodium, and glycogen stores. "
                "We track your 7-day rolling average to observe true body composition trends."
            )

        # 5. Intent: Progress Analysis ("how is my progress", "weekly progress", "analyze progress", "am i on track")
        elif re.search(r'\b(progress|on track|weekly review|how am i doing|analyze|summary)\b', msg_lower):
            prog_res = cls.execute_tool(db, user_id, "analyze_progress", {})
            executed_tools.append({"name": "analyze_progress", "args": {}, "result": prog_res})

            if "adherence" in prog_res:
                adh = prog_res["adherence"]
                avg = prog_res["averages"]
                rec = prog_res["recommendation"]
                assistant_reply = (
                    f"📊 **Weekly Progress Analysis**\n\n"
                    f"- **Days Logged:** {prog_res['days_logged']} days\n"
                    f"- **Calorie Adherence:** {adh['calorie_adherence_pct']}% ({adh['consistency_rating']})\n"
                    f"- **Daily Calories Avg:** {int(avg['daily_calories'])} / {int(avg['target_calories'])} kcal\n"
                    f"- **Daily Protein Avg:** {int(avg['daily_protein_g'])} / {int(avg['target_protein_g'])} g\n"
                    f"- **Weight Trend:** {prog_res['weight_analysis']['trend'].title()} ({prog_res['weight_analysis']['weekly_rate_kg']} kg/week)\n\n"
                    f"💡 **AI Coach Recommendation:**\n{rec['text']}"
                )
            else:
                assistant_reply = prog_res.get("error", "Not enough data yet to analyze weekly progress.")

        # 6. Intent: Scientific RAG Questions ("what is protein", "foods contain iron", "what does fiber do", "calcium")
        elif re.search(r'\b(what is|what does|why is|foods contain|sources of|calcium|fiber|iron|research|evidence|studies|guidelines)\b', msg_lower):
            rag_args = {"query": user_message}
            rag_res = cls.execute_tool(db, user_id, "retrieve_nutrition_evidence", rag_args)
            executed_tools.append({"name": "retrieve_nutrition_evidence", "args": rag_args, "result": rag_res})

            assistant_reply = (
                f"📚 **Scientific Nutrition Evidence**\n\n"
                f"{rag_res['answer']}\n\n"
                f"**Source Document:** {rag_res['document']} ({rag_res['source']})\n"
                f"**Confidence:** {int(rag_res['confidence'] * 100)}%\n\n"
                f"*{rag_res['disclaimer']}*"
            )

        # 7. Intent: Food Search ("calories in banana", "search roti", "nutrition of eggs")
        elif re.search(r'\b(calories in|nutrition of|search food|how many calories|protein in)\b', msg_lower):
            q_clean = re.sub(r'\b(calories in|nutrition of|search food|how many calories in|protein in|what are the)\b', '', msg_lower).strip()
            s_args = {"query": q_clean or "roti"}
            s_res = cls.execute_tool(db, user_id, "search_food", s_args)
            executed_tools.append({"name": "search_food", "args": s_args, "result": s_res})

            res_list = s_res.get("results", [])
            if res_list:
                f = res_list[0]
                assistant_reply = (
                    f"🔍 **Nutritional Information for {f['name']}**\n\n"
                    f"- **Serving Size:** {f['serving_size']}\n"
                    f"- **Calories:** {f['calories']} kcal\n"
                    f"- **Protein:** {f['protein_g']} g\n"
                    f"- **Carbohydrates:** {f['carbs_g']} g\n"
                    f"- **Fat:** {f['fat_g']} g\n"
                    f"- **Fiber:** {f['fiber_g']} g\n"
                )
            else:
                assistant_reply = f"Could not find nutritional data for '{q_clean}'. You can create a custom food in the Food Database."

        # Default: Personalized Contextual Response
        else:
            profile_res = cls.execute_tool(db, user_id, "get_user_profile", {})
            executed_tools.append({"name": "get_user_profile", "args": {}, "result": profile_res})
            daily_res = cls.execute_tool(db, user_id, "get_daily_food_log", {})
            executed_tools.append({"name": "get_daily_food_log", "args": {}, "result": daily_res})

            user_name = profile_res.get("name", "there")
            target_cals = profile_res.get("target_calories", 2000)
            rem_cals = daily_res.get("metrics", {}).get("calories", {}).get("remaining", target_cals)
            rem_prot = daily_res.get("metrics", {}).get("protein", {}).get("remaining", 70)

            assistant_reply = (
                f"Hello {user_name}! I am your Personal AI Nutrition Coach.\n\n"
                f"Here is your status for today:\n"
                f"- **Remaining Calories:** {int(rem_cals)} / {int(target_cals)} kcal\n"
                f"- **Remaining Protein:** {int(rem_prot)}g\n\n"
                f"You can ask me to:\n"
                f"1. Log meals (e.g. *'I had 2 rotis and 1 bowl dal'*)\n"
                f"2. Generate meal plans (e.g. *'Give me a high-protein dinner'*)\n"
                f"3. Suggest substitutions (e.g. *'Replace paneer with chicken'*)\n"
                f"4. Ask science questions (e.g. *'What foods contain iron?'*)\n"
                f"5. Log scale weight (e.g. *'Log weight 72.5 kg'*)\n"
                f"6. Review weekly progress (e.g. *'How is my progress this week?'*)"
            )

        # Save assistant message
        db.add(ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assistant_reply,
            tool_calls=json.dumps([{"name": t["name"], "args": t["args"]} for t in executed_tools]),
            tool_results=json.dumps([{"name": t["name"], "result": t["result"]} for t in executed_tools])
        ))
        db.commit()

        return {
            "role": "assistant",
            "content": assistant_reply,
            "tool_calls_executed": executed_tools
        }

    @classmethod
    async def _chat_with_external_llm(
        cls,
        db: Session,
        user_id: int,
        session_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Executes external LLM with standard tool calling protocol.
        """
        base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json"
        }

        # Build message history
        past_msgs = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.id.desc()).limit(10).all()
        past_msgs.reverse()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in past_msgs:
            messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": settings.LLM_MODEL or "gpt-4o-mini",
            "messages": messages,
            "tools": AGENT_TOOLS,
            "tool_choice": "auto"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]

            executed_tools = []

            # Check if LLM requested tool calling
            if "tool_calls" in msg and msg["tool_calls"]:
                tool_calls = msg["tool_calls"]
                tool_messages = [msg]

                for tc in tool_calls:
                    fname = tc["function"]["name"]
                    fargs = json.loads(tc["function"].get("arguments", "{}"))
                    result = cls.execute_tool(db, user_id, fname, fargs)
                    executed_tools.append({"name": fname, "args": fargs, "result": result})

                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fname,
                        "content": json.dumps(result)
                    })

                # Follow-up request to LLM to formulate personalized reply with tool results
                second_payload = {
                    "model": settings.LLM_MODEL or "gpt-4o-mini",
                    "messages": messages + tool_messages,
                }
                sec_resp = await client.post(f"{base_url}/chat/completions", json=second_payload, headers=headers)
                sec_resp.raise_for_status()
                final_content = sec_resp.json()["choices"][0]["message"]["content"]
            else:
                final_content = msg.get("content", "I am here to help with your nutrition.")

            # Save assistant message
            db.add(ChatMessage(
                session_id=session_id,
                role="assistant",
                content=final_content,
                tool_calls=json.dumps([{"name": t["name"], "args": t["args"]} for t in executed_tools]),
                tool_results=json.dumps([{"name": t["name"], "result": t["result"]} for t in executed_tools])
            ))
            db.commit()

            return {
                "role": "assistant",
                "content": final_content,
                "tool_calls_executed": executed_tools
            }
