from fastapi import APIRouter, Depends, HTTPException
from app.services.rules_services import RuleService
from app.services.ai_model_services import ZeroShotClassifier
from app.services.filtering_service import EmailFilteringService
from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient
from app.schemas.filtering_schema import FilterRequest, FilterResponse, FilterResult, RunFilterRequest
from app.models.rules_model import RuleModel

router = APIRouter(
    prefix="/filter",
    tags=["Filtering"]
)

def get_rule_service():
    return RuleService()

def get_classifier():
    return ZeroShotClassifier()

def get_google_auth_handler():
    return GoogleAuthHandler()

def get_gmail_client(auth_handler: GoogleAuthHandler = Depends(get_google_auth_handler)):
    return GmailClient(auth_handler=auth_handler)

def get_email_filtering_service(
    rule_service: RuleService = Depends(get_rule_service),
    classifier: ZeroShotClassifier = Depends(get_classifier)
):
    return EmailFilteringService(rule_service=rule_service, classifier=classifier)

@router.post("/apply", response_model=FilterResponse)
async def apply_filter(
    request: FilterRequest,
    filtering_service: EmailFilteringService = Depends(get_email_filtering_service),
    rule_service: RuleService = Depends(get_rule_service)
):
    rules_to_apply = [rule_service.get_rule_by_id(rule_id) for rule_id in request.rule_ids]
    rules_to_apply = [rule for rule in rules_to_apply if rule is not None]

    if not rules_to_apply:
        raise HTTPException(status_code=400, detail="No valid rules found for provided IDs.")

    aggregated_score = filtering_service.filter_emails_by_rules(
        email_content=request.email_content,
        rules=rules_to_apply
    )
    
    single_result = FilterResult(
        matched_rule="Aggregated Score",
        score=aggregated_score,
        email_content=request.email_content
    )
    return FilterResponse(results=[single_result])

@router.post("/run", response_model=FilterResponse)
async def run_full_filter(
    request: RunFilterRequest,
    gmail_client: GmailClient = Depends(get_gmail_client),
    filtering_service: EmailFilteringService = Depends(get_email_filtering_service),
    rule_service: RuleService = Depends(get_rule_service)
):
    email_snippets = gmail_client.get_today_emails()
    print(f"found {len(email_snippets)} emails from last 24 hours")
    
    rules_to_apply = [rule_service.get_rule_by_id(rule_id) for rule_id in request.rule_ids]
    rules_to_apply = [rule for rule in rules_to_apply if rule is not None]

    if not rules_to_apply:
        raise HTTPException(status_code=400, detail="No valid rules found for provided IDs.")

    matched_results = []
    for snippet in email_snippets:
        if not snippet:
            continue

        aggregated_score = filtering_service.filter_emails_by_rules(
            email_content=snippet,
            rules=rules_to_apply
        )
        
        storage_threshold = 50.0
        if aggregated_score >= storage_threshold:
            matched_results.append(FilterResult(
                matched_rule="Aggregated Score",
                score=aggregated_score,
                email_content=snippet
            ))

    return FilterResponse(results=matched_results)
