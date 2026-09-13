import json


from backend.app.services.llm_provider import LLMProvider
from ml.taxonomy.intents import get_intent_descriptions


class IntentClassifier:
    def __init__(self):
        self.llm = LLMProvider()
        self.intents = get_intent_descriptions()

    def classify(self, customer_message: str) -> dict:
        if not customer_message or not customer_message.strip():
            raise ValueError("Customer message cannot be empty.")

        intent_text = "\n".join(
            f"- {name}: {description}"
            for name, description in self.intents.items()
        )

        prompt = f"""
You are a customer support intent classifier for AmazonHelp.

Classify the customer message into exactly ONE of these intents:

{intent_text}

Customer message:
{customer_message}

Return ONLY valid JSON in this format:
{{
  "intent": "one_intent_name",
  "confidence": 0.0
}}

Confidence must be between 0 and 1.
Do not include any explanation.
"""

        response = self.llm.generate(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        intent = result.get("intent")
        confidence = float(result.get("confidence", 0))

        if intent not in self.intents:
            raise ValueError(f"Invalid intent returned by LLM: {intent}")

        confidence = max(0.0, min(1.0, confidence))

        return {
            "intent": intent,
            "confidence": confidence,
        }