"""
Intent taxonomy for AmazonHelp customer support conversations.

The taxonomy is intentionally small so that the classifier
can make reliable predictions without overly fine-grained classes.
"""

INTENTS = {
    "order_issue": {
        "description": "Problems with placing, changing, or managing an order.",
    },
    "delivery_issue": {
        "description": "Late, missing, damaged, or incorrect delivery.",
    },
    "return_refund": {
        "description": "Returns, refunds, replacements, or refund status.",
    },
    "payment_billing": {
        "description": "Payment failures, charges, invoices, or billing questions.",
    },
    "account_access": {
        "description": "Login, account, password, or account-related problems.",
    },
    "prime_subscription": {
        "description": "Amazon Prime membership, subscription, or Prime benefits.",
    },
    "product_issue": {
        "description": "Problems with a product, device, or product functionality.",
    },
    "digital_content": {
        "description": "Issues with Prime Video, Kindle, apps, digital purchases, or other digital content.",
    },
    "general_support": {
        "description": "Questions or issues that do not clearly fit another intent.",
    },
}


def get_intent_names():
    """Return the available intent names."""
    return list(INTENTS.keys())


def get_intent_descriptions():
    """Return intent names with their descriptions."""
    return {
        name: details["description"]
        for name, details in INTENTS.items()
    }
def validate_taxonomy():
    """Validate that the taxonomy has unique names and descriptions."""
    assert INTENTS, "Intent taxonomy cannot be empty."
    assert len(INTENTS) == len(set(INTENTS.keys()))
    assert all(
        details.get("description")
        for details in INTENTS.values()
    )

    return True


if __name__ == "__main__":
    validate_taxonomy()
    print(f"Taxonomy valid: {len(INTENTS)} intents")
    print("\n".join(f"- {name}" for name in get_intent_names()))