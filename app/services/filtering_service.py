from app.services.rules_services import RuleService
from app.services.ai_model_services import ZeroShotClassifier
from app.models.rules_model import RuleModel
from typing import List, Dict, Optional

class EmailFilteringService:
    def __init__(self, rule_service: RuleService, classifier: ZeroShotClassifier):
        self.rule_service = rule_service
        self.classifier = classifier
        self.individual_match_threshold = 0.5

    def filter_emails_by_rules(self, email_content: str, rules: List[RuleModel]) -> float:
        overall_score = 0.0
        
        for rule in rules:
            branch_score, high_exists_in_branch, high_matched_in_branch = self._evaluate_rule_branch(email_content, rule)
            
            overall_score += branch_score 

        return min(overall_score, 100.0)

    def _evaluate_rule_branch(self, email_content: str, rule: RuleModel) -> (float, bool, bool):
        score_from_this_rule = 0.0
        high_priority_exists_in_branch = False
        high_priority_matched_in_branch = False

        classification_results = self.classifier.classify(email_content, [rule.description])
        
        if classification_results and classification_results.get('scores') and len(classification_results['scores']) > 0:
            match_score = classification_results['scores'][0]
            is_matched = match_score >= self.individual_match_threshold

            if rule.priority == "High":
                high_priority_exists_in_branch = True
                if is_matched:
                    high_priority_matched_in_branch = True
                    score_from_this_rule += 30.0
                else: 
                    pass
            elif rule.priority == "Low":
                if is_matched:
                    score_from_this_rule += 20.0
                else:
                    pass
            
        total_branch_score = score_from_this_rule 

        if rule.sub_rules:
            for sub_rule in rule.sub_rules:
                sub_score, sub_high_exists, sub_high_matched = self._evaluate_rule_branch(email_content, sub_rule)
                total_branch_score += sub_score 
                
                if sub_high_exists:
                    high_priority_exists_in_branch = True
                if sub_high_matched:
                    high_priority_matched_in_branch = True

        return total_branch_score, high_priority_exists_in_branch, high_priority_matched_in_branch