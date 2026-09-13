from backend.app.services.llm_provider import LLMProvider


class ResponseGenerator:
    def __init__(self):
        self.llm = LLMProvider()

    def generate(
        self,
        customer_message: str,
        intent: str,
        historical_examples: list[dict],
    ) -> str:
        evidence = "\n\n".join(
            f"Historical customer: {item['customer_text']}\n"
            f"Historical AmazonHelp response: {item['agent_response']}"
            for item in historical_examples
        )

        prompt = f"""
You are an AmazonHelp customer support agent.

Customer message:
{customer_message}

Detected intent:
{intent}

Historical examples from AmazonHelp:
{evidence}

Write a helpful, concise support reply grounded in the historical examples.

Rules:
- Do not invent policies, refunds, links, or actions.
- Use the historical responses as evidence.
- Do not mention that you are an AI.
- Do not copy a historical response verbatim unless necessary.
- If the historical evidence is insufficient, say so clearly and avoid guessing.
- Return only the customer-facing reply.
"""

        return self.llm.generate(prompt)