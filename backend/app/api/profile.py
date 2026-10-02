from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.nutrition_calculator import NutritionCalculator
from app.services.progress_analyzer import ProgressAnalyzer

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT /api/profile to update."
        )

    # Compute deterministic targets
    calc = NutritionCalculator.calculate_all(
        weight_kg=profile_in.current_weight_kg,
        height_cm=profile_in.height_cm,
        age=profile_in.age,
        sex=profile_in.sex,
        activity_level=profile_in.activity_level,
        goal=profile_in.goal
    )

    profile = Profile(
        user_id=current_user.id,
        name=profile_in.name,
        age=profile_in.age,
        sex=profile_in.sex,
        height_cm=profile_in.height_cm,
        current_weight_kg=profile_in.current_weight_kg,
        target_weight_kg=profile_in.target_weight_kg,
        activity_level=profile_in.activity_level,
        goal=profile_in.goal,
        diet_type=profile_in.diet_type,
        food_preferences=profile_in.food_preferences or "",
        foods_disliked=profile_in.foods_disliked or "",
        allergies=profile_in.allergies or "",
        budget=profile_in.budget or "moderate",
        meal_count=profile_in.meal_count or 4,
        meal_times=profile_in.meal_times or "08:30,13:00,17:00,20:30",
        cooking_time=profile_in.cooking_time or "30_mins",
        exercise_frequency=profile_in.exercise_frequency or "3_4_days",
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
    db.refresh(profile)

    # Log initial weight
    ProgressAnalyzer.log_weight(
        db=db,
        user_id=current_user.id,
        weight_kg=profile_in.current_weight_kg,
        note="Initial onboarding weight"
    )

    return profile


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding first."
        )
    return profile


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding first."
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    # Recalculate deterministic targets
    calc = NutritionCalculator.calculate_all(
        weight_kg=profile.current_weight_kg,
        height_cm=profile.height_cm,
        age=profile.age,
        sex=profile.sex,
        activity_level=profile.activity_level,
        goal=profile.goal
    )

    profile.bmr = calc["bmr"]
    profile.tdee = calc["tdee"]
    profile.target_calories = calc["target_calories"]
    profile.target_protein_g = calc["target_protein_g"]
    profile.target_carbs_g = calc["target_carbs_g"]
    profile.target_fat_g = calc["target_fat_g"]
    profile.target_fiber_g = calc["target_fiber_g"]
    profile.target_water_ml = calc["target_water_ml"]

    db.commit()
    db.refresh(profile)
    return profile
