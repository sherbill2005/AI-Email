# app/serviceHandler/summarizer_handler.py

from app.services.orchestration_service import EmailProcessingOrchestrator


class SummarizerHandler:
    def __init__(self):
        self.orchestrator = EmailProcessingOrchestrator()

    def handle(self, email_index: int) -> str:
        return self.orchestrator.summarize_by_index(email_index)



