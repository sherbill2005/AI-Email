from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from app.schemas.rules_schema import RuleResponse, RuleCreate, RuleUpdate
from app.services.rules_services import RuleService

router = APIRouter()

def get_rule_service():
    return RuleService()
@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(rule_service: RuleService = Depends(get_rule_service)):
    return rule_service.get_all_rules()


@router.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate, rule_service: RuleService = Depends(get_rule_service)):
    return rule_service.create_rule(rule)

@router.get("/rules/{id}", response_model=RuleResponse)
async def get_rule_by_id(rule_id: str, rule_service: RuleService= Depends(get_rule_service)):
    rule = rule_service.get_rule_by_id(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
@router.put("/rules/{id}", response_model=RuleResponse)
async def update_rule(rule_id:str, rule_update: RuleUpdate, rule_service: RuleService = Depends(get_rule_service)):
        updated_rule = rule_service.update_rule(rule_id, rule_update)
        if updated_rule is None:
            raise HTTPException(status_code=404, detail="Rule not found")
        return updated_rule

@router.delete("/rules/{id}", status_code=status.HTTP_200_OK)
async def delete_rule(rule_id: str, rule_service: RuleService = Depends(get_rule_service)):
    deleted = rule_service.delete_rule(rule_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return None
