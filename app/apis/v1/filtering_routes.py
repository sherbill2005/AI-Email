from fastapi import APIRouter, Depends
from app.services.rules_services import RuleService
from app.services.ai_model_services import ZeroShotClassifier
from app.services.filtering_service import EmailFilteringService
from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient
from app.schemas.filtering_schema import FilterRequest, FilterResponse, FilterResult, RunFilterRequest

router = APIRouter(
    prefix="/filter",
    tags=["Filtering"]
)

# --- Dependency Injection Setup ---

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


# --- Endpoint Definitions ---

# Endpoint 1: Applies rules to a single piece of text provided by the user
@router.post("/apply", response_model=FilterResponse)
async def apply_filter(
    request: FilterRequest,
    filtering_service: EmailFilteringService = Depends(get_email_filtering_service)
):
    result_dict = filtering_service.filter_emails_by_rules(
        email_content=request.email_content,
        rule_ids=request.rule_ids
    )
    result_dict['email_content'] = request.email_content
    single_result = FilterResult(**result_dict)
    return FilterResponse(results=[single_result])


# Endpoint 2: Fetches today's emails from Gmail and applies rules
@router.post("/run", response_model=FilterResponse)
async def run_full_filter(
    request: RunFilterRequest,
    gmail_client: GmailClient = Depends(get_gmail_client),
    filtering_service: EmailFilteringService = Depends(get_email_filtering_service)
):
    email_snippets = gmail_client.get_today_emails()
    print(f"found {len(email_snippets)} emails from last 24 hours")
    matched_results = []
    for snippet in email_snippets:
        if not snippet:
            continue

        result_dict = filtering_service.filter_emails_by_rules(
            email_content=snippet,  # Use the snippet from the loop
            rule_ids=request.rule_ids
        )
        if result_dict:
            print(f"Email: '{snippet[:100]}...' --> score: {result_dict.get('score'):.2f} for Rule:'{result_dict.get('matched_rule')}'")
        if result_dict and result_dict.get('score', 0) > 0.6:
            result_dict['email_content'] = snippet
            matched_results.append(FilterResult(**result_dict))

    return FilterResponse(results=matched_results)