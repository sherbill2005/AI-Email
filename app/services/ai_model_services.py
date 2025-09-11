# app/services/ai_model_services.py

from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate


class LangchainSummarizer:
    def __init__(self):
       
        hf_pipeline = pipeline(
            task="summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )
        self.summarizer = HuggingFacePipeline(
            pipeline=hf_pipeline,
            model_kwargs={
                "temperature": 0.7,
                "max_length": 100
            }
        )

    def summarize_email(self, content: str) -> str:

        return self.summarizer.invoke(content)





class ZeroShotClassifier:
    def __init__(self):
        classification_pipeline = pipeline(
        task = "zero-shot-classification",
        model= "facebook/bart-large-mnli"
        )
        self.classifier = HuggingFacePipeline(
            pipeline=classification_pipeline,
        )

    def classify(self , email_content: str, labels: list[str]):
        if not email_content or not labels:
            return {'labels': [], 'scores':[]}
        results = self.classifier.pipeline(email_content, candidate_labels=labels)
        return {'labels': results['labels'], 'scores': results['scores']}
if __name__ == "__main__":
    handler = LangchainSummarizer()
    test_email = (
        "To fall asleep faster and sleep better, establish a regular sleep schedule..."
    )
    print(handler.summarize_email(test_email))