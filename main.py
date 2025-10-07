from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.apis.v1.routes import router as summarize_router
from app.apis.v1.rules_routes import router as summarize_rules_router
from app.apis.v1.filtering_routes import router as filtering_router
from app.apis.v1.gmail_webhook import router as webhook_router
from app.apis.v1.auth_routes import router as auth_router

app = FastAPI(
    title="AI Email Summarizer",
    version="1.0.0",
    description="Summarizes emails using AI",
)

# Define allowed origins for CORS
origins = [
    "http://localhost:3000",  # Standard React dev server
    "http://localhost:5173",  # Standard Vite dev server
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summarize_router, prefix='/apis/v1')
app.include_router(summarize_rules_router, prefix='/apis/v1', tags=["Rules"])
app.include_router(filtering_router, prefix='/apis/v1')
app.include_router(webhook_router, prefix='/apis/v1', tags=["Webhook"])
app.include_router(auth_router, prefix='/apis/v1')

@app.get('/')
async def root():
    return {"message": "Welcome to AI Email Summarizer"}