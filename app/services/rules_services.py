from bson import ObjectId
from typing import Optional, List

from app.db_utils.mongo import db
from app.models.rules_model import RuleModel
from app.schemas.rules_schema import RuleCreate, RuleUpdate


class RuleService:
    def __init__(self):
        self.collection = db['rules']

    def get_all_rules(self) -> List[RuleModel]:
        rules_cursor = self.collection.find()
        rules = []
        for rule in rules_cursor:
            rule['_id'] = str(rule['_id'])
            rules.append(RuleModel(**rule))
        return rules

    def get_rule_by_id(self, rule_id: str) -> RuleModel|None:
        rule_data = self.collection.find_one({'_id':ObjectId(rule_id)})
        if rule_data:
            rule_data['_id'] = str(rule_data['_id'])
            return RuleModel(**rule_data)
        return None

    def create_rule(self, rule: RuleCreate) -> RuleModel|None:
        rule_data = rule.model_dump()
        result = self.collection.insert_one(rule_data)
        new_rule = self.collection.find_one({'_id':result.inserted_id})
        if new_rule:
            new_rule['_id'] = str(new_rule['_id'])
            return RuleModel(**new_rule)
        return None


    def update_rule(self, rule_id: str ,rule: RuleUpdate) -> RuleModel | None:
        obj_id = ObjectId(rule_id)
        updated_data = rule.model_dump(exclude_unset=True)
        if not updated_data:
            return self.get_rule_by_id(rule_id)

        self.collection.update_one(
            {'_id':obj_id},
            {'$set':updated_data}
        )
        return self.get_rule_by_id(rule_id)

    def delete_rule(self, rule_id: str) -> bool:
        result = self.collection.delete_one({'_id':ObjectId(rule_id)})
        return result.deleted_count > 0