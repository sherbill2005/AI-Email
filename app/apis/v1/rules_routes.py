from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from app.schemas.rules_schema import RuleResponse, RuleCreate, RuleUpdate
from app.services.rules_services import RuleService
from app.services.auth_services import get_current_user
from app.models.user_model import User

router = APIRouter()

def get_rule_service():
    return RuleService()

@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(rule_service: RuleService = Depends(get_rule_service), current_user: User = Depends(get_current_user)):
    return rule_service.get_all_rules(user_id=str(current_user._id))

@router.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate, rule_service: RuleService = Depends(get_rule_service), current_user: User = Depends(get_current_user)):
    return rule_service.create_rule(rule, user_id=str(current_user._id))

@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule_by_id(rule_id: str, rule_service: RuleService = Depends(get_rule_service), current_user: User = Depends(get_current_user)):
    rule = rule_service.get_rule_by_id(rule_id, user_id=str(current_user._id))
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str, rule_update: RuleUpdate, rule_service: RuleService = Depends(get_rule_service), current_user: User = Depends(get_current_user)):
    updated_rule = rule_service.update_rule(rule_id, rule_update, user_id=str(current_user._id))
    if updated_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated_rule

@router.delete("/rules/{rule_id}", status_code=status.HTTP_200_OK)
async def delete_rule(rule_id: str, rule_service: RuleService = Depends(get_rule_service), current_user: User = Depends(get_current_user)):
    deleted = rule_service.delete_rule(rule_id, user_id=str(current_user._id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found or you do not have permission to delete it")
    return None
