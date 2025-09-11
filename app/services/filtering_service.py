from app.services.rules_services import RuleService
from app.services.ai_model_services import ZeroShotClassifier

class EmailFilteringService:
    def __init__(self, rule_service: RuleService, classifier: ZeroShotClassifier):
        self.rule_service = rule_service
        self.classifier = classifier

    def filter_emails_by_rules(self, email_content: str, rule_ids: list[str], threshold: float = 0.8) -> list[dict]:
        """
        Filters a single email against a list of specified rules, returning scores for each.

        Args:
            email_content: The text content of the email to filter.
            rule_ids: A list of rule IDs to filter against.
            threshold: The confidence score threshold for a rule to be considered 'matched'.

        Returns:
            A list of dictionaries, each containing rule_name, score, and classification.
        """
        # Step 1: Get rule descriptions from the database
        rules_data = []
        for rule_id in rule_ids:
            rule = self.rule_service.get_rule_by_id(rule_id)
            if rule:
                rules_data.append({"id": rule.id, "name": rule.name, "description": rule.description})

        if not rules_data:
            return []

        labels = [rule["description"] for rule in rules_data]

        # Step 2: Use the classifier to get scores
        classification_results = self.classifier.classify(email_content, labels)

        if not classification_results or not classification_results.get('scores'):
            return []

        # Step 3: Format results for all rules
        formatted_scores = []
        for i, label_description in enumerate(classification_results['labels']):
            score = classification_results['scores'][i]
            # Find the original rule name based on description
            original_rule = next((r for r in rules_data if r["description"] == label_description), None)
            rule_name = original_rule["name"] if original_rule else label_description # Fallback

            classification = "Matched" if score >= threshold else "Not Matched"

            formatted_scores.append({
                "rule_name": rule_name,
                "score": round(float(score), 4), # Ensure float and round for consistency
                "classification": classification
            })
        return formatted_scores
