from app.services.ai_model_services import LangchainSummarizer

handler = LangchainSummarizer()
subject = handler.summarize_email(content='o fall asleep faster and sleep better, establish a regular sleep schedule, create a relaxing bedtime routine, and optimize your sleep environment. Limit caffeine and alcohol, especially before bed, and avoid screens at least an hour before sleep. Consider relaxation techniques like deep breathing or meditation to help unwind')
print(subject)