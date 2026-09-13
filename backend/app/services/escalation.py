class EscalationService:
    """
    Decides whether a support request can be auto-handled
    or should be reviewed by a human.
    """

    CONFIDENCE_THRESHOLD = 0.75
    MIN_EVIDENCE_SCORE = 0.65

    def decide(
        self,
        intent: str,
        confidence: float,
        historical_examples: list[dict],
    ) -> dict:
        if confidence < self.CONFIDENCE_THRESHOLD:
            return {
                "decision": "escalate",
                "reason": "Intent confidence is below the auto-handle threshold.",
            }

        if not historical_examples:
            return {
                "decision": "escalate",
                "reason": "No historical support evidence was retrieved.",
            }

        best_score = historical_examples[0].get("score", 0.0)

        if best_score < self.MIN_EVIDENCE_SCORE:
            return {
                "decision": "escalate",
                "reason": "Retrieved historical evidence is not sufficiently similar.",
            }

        return {
            "decision": "auto_handle",
            "reason": "Intent confidence and historical evidence meet the auto-handle thresholds.",
        }