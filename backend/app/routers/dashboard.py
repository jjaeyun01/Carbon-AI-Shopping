from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard():
    return {
        "total_carbon_saved": 18.4,
        "eco_choices_made": 7,
        "better_alternatives_chosen": 5,
        "sustainability_score": 84,
        "monthly_savings_kg": 6.2,
        "best_category": "Clothing",
        "average_eco_score": 26,
        "saved_items": 12
    }