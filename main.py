from fastapi import FastAPI
from app.apis.v1.routes import router as summarize_router
from app.apis.v1.rules_routes import router as summarize_rules_router
from app.apis.v1.filtering_routes import router as filtering_router
from app.apis.v1.gmail_webhook import router as webhook_router

app = FastAPI(
    title="AI Email Summarizer",
    version="1.0.0",
    description="Summarizes emails using AI",

)

app.include_router(summarize_router, prefix='/apis/v1')
app.include_router(summarize_rules_router, prefix='/apis/v1', tags=["Rules"])
app.include_router(filtering_router, prefix='/apis/v1')
app.include_router(webhook_router, prefix='/apis/v1', tags=["Webhook"])

@app.get('/')
async def root():
    return {"message": "Welcome to AI Email Summarizer"}
