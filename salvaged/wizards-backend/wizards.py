from database import get_db
from fastapi import APIRouter, Depends
from models.subscription import Subscription
from models.user import User
from sqlalchemy.orm import Session

from services.auth_service import get_current_user
from services.empathy_service import EmpathyService

"""
Wizards API endpoints
"""


router = APIRouter()


@router.get("/list")
async def list_wizards(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get list of available wizards based on user's subscription tier"""
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()

    if not subscription:
        return {"wizards": [], "available_wizards": []}

    empathy_service = EmpathyService()
    all_wizards = empathy_service.get_available_wizards()
    available_wizard_names = subscription.get_available_wizards()

    # Mark which wizards are available
    for wizard in all_wizards:
        wizard["available"] = wizard["name"] in available_wizard_names

    return {
        "tier": subscription.tier.value,
        "wizards": all_wizards,
        "available_wizards": available_wizard_names,
    }


@router.get("/{wizard_name}")
async def get_wizard_info(wizard_name: str, current_user: User = Depends(get_current_user)):
    """Get detailed information about a specific wizard"""
    empathy_service = EmpathyService()
    all_wizards = empathy_service.get_available_wizards()

    wizard = next((w for w in all_wizards if w["name"] == wizard_name), None)

    if not wizard:
        return {"error": "Wizard not found"}

    return wizard
