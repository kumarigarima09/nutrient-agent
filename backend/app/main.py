"""
Main FastAPI Application Entrypoint
Initializes Database tables, pre-seeds Indian food composition & scientific RAG datasets,
configures CORS middleware, and mounts all typed API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models import *  # noqa: F401, F403
from app.models.user import User
from app.models.profile import Profile
from app.services.food_service import FoodService
from app.services.rag_service import RAGRetriever
from app.services.nutrition_calculator import NutritionCalculator
from app.services.progress_analyzer import ProgressAnalyzer

# Import API Routers
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.nutrition import router as nutrition_router
from app.api.foods import router as foods_router
from app.api.meals import router as meals_router
from app.api.food_log import router as food_log_router
from app.api.weight import router as weight_router
from app.api.meal_plan import router as meal_plan_router
from app.api.chat import router as chat_router
from app.api.food_image import router as food_image_router
from app.api.progress import router as progress_router
from app.api.dashboard import router as dashboard_router
from app.api.rag import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed food database
        food_count = FoodService.seed_initial_foods(db)

        # 2. Seed RAG evidence documents
        rag_count = RAGRetriever.seed_evidence_documents(db)

        # 3. Create demo user and profile if empty
        user = db.query(User).filter(User.email == "demo@nutritionagent.ai").first()
        if not user:
            user = User(
                email="demo@nutritionagent.ai",
                full_name="Aarav Sharma",
                hashed_password=get_password_hash("demo1234"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if not profile:
            # Deterministic calculation for initial profile
            calc = NutritionCalculator.calculate_all(
                weight_kg=76.0,
                height_cm=175.0,
                age=29,
                sex="male",
                activity_level="moderate",
                goal="weight_loss"
            )
            profile = Profile(
                user_id=user.id,
                name="Aarav Sharma",
                age=29,
                sex="male",
                height_cm=175.0,
                current_weight_kg=76.0,
                target_weight_kg=70.0,
                activity_level="moderate",
                goal="weight_loss",
                diet_type="vegetarian",
                food_preferences="Paneer, Dal, Curd, Poha, Fruits",
                foods_disliked="Bitter gourd",
                allergies="",
                budget="moderate",
                meal_count=4,
                meal_times="08:30,13:00,17:00,20:30",
                cooking_time="30_mins",
                exercise_frequency="4_days_strength",
                bmr=calc["bmr"],
                tdee=calc["tdee"],
                target_calories=calc["target_calories"],
                target_protein_g=calc["target_protein_g"],
                target_carbs_g=calc["target_carbs_g"],
                target_fat_g=calc["target_fat_g"],
                target_fiber_g=calc["target_fiber_g"],
                target_water_ml=calc["target_water_ml"],
            )
            db.add(profile)
            db.commit()

            # Seed historical weight logs for instant visual sparkline
            ProgressAnalyzer.log_weight(db, user.id, 77.2, "2026-09-24", "Morning weigh-in")
            ProgressAnalyzer.log_weight(db, user.id, 76.9, "2026-09-26", "Post-workout")
            ProgressAnalyzer.log_weight(db, user.id, 76.5, "2026-09-28", "Fasted")
            ProgressAnalyzer.log_weight(db, user.id, 76.0, "2026-09-30", "Weekly milestone")

    finally:
        db.close()

    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal AI Nutrition Agent Backend with Deterministic Nutrition Engines and Tool Calling",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(nutrition_router, prefix="/api")
app.include_router(foods_router, prefix="/api")
app.include_router(meals_router, prefix="/api")
app.include_router(food_log_router, prefix="/api")
app.include_router(weight_router, prefix="/api")
app.include_router(meal_plan_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(food_image_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(rag_router, prefix="/api")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Access documentation at /docs."
    }
