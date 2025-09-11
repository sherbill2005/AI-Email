from fastapi import APIRouter, HTTPException
from app.schemas.email_schema import SummarizeRequest, SummarizeResponse
from app.services.service_handler import SummarizerHandler

router = APIRouter()


@router.post('/summarize', response_model=SummarizeResponse)
async def summarize_email(request: SummarizeRequest):
    handle = SummarizerHandler()
    summary = handle.handle(request.email_index)
    # print(summary)
    return SummarizeResponse(summaries=summary)
