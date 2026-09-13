from backend.app.services.classifier import IntentClassifier
from backend.app.services.retriever import RetrievalService
from backend.app.services.generator import ResponseGenerator
from backend.app.services.escalation import EscalationService


class SupportAgent:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.retriever = RetrievalService()
        self.generator = ResponseGenerator()
        self.escalation = EscalationService()

    def handle(self, customer_message: str) -> dict:
        if not customer_message or not customer_message.strip():
            raise ValueError("Customer message cannot be empty.")

        classification = self.classifier.classify(customer_message)

        historical_examples = self.retriever.search(
            customer_message,
            top_k=5,
        )

        decision = self.escalation.decide(
            intent=classification["intent"],
            confidence=classification["confidence"],
            historical_examples=historical_examples,
        )

        draft_reply = self.generator.generate(
            customer_message=customer_message,
            intent=classification["intent"],
            historical_examples=historical_examples,
        )

        return {
            "customer_message": customer_message,
            "intent": classification["intent"],
            "confidence": classification["confidence"],
            "decision": decision["decision"],
            "escalation_reason": decision["reason"],
            "draft_reply": draft_reply,
            "historical_evidence": historical_examples,
        }