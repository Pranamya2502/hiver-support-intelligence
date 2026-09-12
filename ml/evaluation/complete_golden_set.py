"""
Complete and validate the 200-example golden evaluation set.

This script populates gold_intent, gold_escalate, and label_notes for all 200
examples in data/golden/golden_set.csv using the locked 9-intent taxonomy
and escalation rules.

It enforces strict validation checks to ensure zero missing labels, zero text
modifications, and valid taxonomy values.
"""

from pathlib import Path
import sys
import pandas as pd

# Add repository root to python path to allow importing ml modules
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.taxonomy.intents import get_intent_names

GOLDEN_PATH = REPO_ROOT / "data" / "golden" / "golden_set.csv"
SAMPLE_SIZE = 200

# Locked 200-example ground truth annotations
# Key: index (0-199) in golden_set.csv
# Value: (gold_intent, gold_escalate, label_notes)
GOLDEN_ANNOTATIONS = {
    0: ("delivery_issue", "false", "Delayed package, routine issue"),
    1: ("delivery_issue", "false", "Delivery status or delay issue"),
    2: ("account_access", "true", "Account hold or access issue"),
    3: ("return_refund", "true", "Refund or return request"),
    4: ("general_support", "false", "General customer inquiry or complaint"),
    5: ("order_issue", "true", "Order placement or management issue"),
    6: ("delivery_issue", "false", "Delivery status or delay issue"),
    7: ("delivery_issue", "false", "Delivery status or delay issue"),
    8: ("delivery_issue", "false", "Delivery status or delay issue"),
    9: ("product_issue", "true", "Physical product or device issue"),
    10: ("delivery_issue", "true", "Delivery status or delay issue"),
    11: ("general_support", "false", "General customer inquiry or complaint"),
    12: ("delivery_issue", "true", "Delivery status or delay issue"),
    13: ("return_refund", "false", "Refund or return request"),
    14: ("payment_billing", "true", "Payment or billing issue"),
    15: ("general_support", "false", "General customer inquiry or complaint"),
    16: ("digital_content", "false", "Digital content or streaming issue"),
    17: ("order_issue", "true", "Order placement or management issue"),
    18: ("order_issue", "true", "Order placement or management issue"),
    19: ("general_support", "true", "General customer inquiry or complaint"),
    20: ("general_support", "false", "General customer inquiry or complaint"),
    21: ("general_support", "true", "General customer inquiry or complaint"),
    22: ("digital_content", "false", "Digital content or streaming issue"),
    23: ("general_support", "false", "General customer inquiry or complaint"),
    24: ("general_support", "false", "General customer inquiry or complaint"),
    25: ("general_support", "false", "General customer inquiry or complaint"),
    26: ("general_support", "true", "General customer inquiry or complaint"),
    27: ("delivery_issue", "true", "Delivery status or delay issue"),
    28: ("return_refund", "false", "Refund or return request"),
    29: ("delivery_issue", "false", "Delivery status or delay issue"),
    30: ("general_support", "false", "General customer inquiry or complaint"),
    31: ("general_support", "false", "General customer inquiry or complaint"),
    32: ("delivery_issue", "false", "Delivery status or delay issue"),
    33: ("general_support", "false", "General customer inquiry or complaint"),
    34: ("payment_billing", "false", "Payment or billing issue"),
    35: ("general_support", "true", "General customer inquiry or complaint"),
    36: ("order_issue", "true", "Order placement or management issue"),
    37: ("payment_billing", "false", "Payment or billing issue"),
    38: ("general_support", "false", "General customer inquiry or complaint"),
    39: ("general_support", "true", "General customer inquiry or complaint"),
    40: ("general_support", "false", "General customer inquiry or complaint"),
    41: ("general_support", "false", "General customer inquiry or complaint"),
    42: ("digital_content", "false", "Digital content or streaming issue"),
    43: ("delivery_issue", "false", "Delivery status or delay issue"),
    44: ("general_support", "true", "General customer inquiry or complaint"),
    45: ("delivery_issue", "false", "Delivery status or delay issue"),
    46: ("general_support", "false", "General customer inquiry or complaint"),
    47: ("delivery_issue", "false", "Delivery status or delay issue"),
    48: ("delivery_issue", "false", "Delivery status or delay issue"),
    49: ("return_refund", "true", "Refund or return request"),
    50: ("general_support", "false", "General customer inquiry or complaint"),
    51: ("general_support", "false", "General customer inquiry or complaint"),
    52: ("general_support", "true", "General customer inquiry or complaint"),
    53: ("delivery_issue", "false", "Delivery status or delay issue"),
    54: ("general_support", "true", "General customer inquiry or complaint"),
    55: ("general_support", "false", "General customer inquiry or complaint"),
    56: ("delivery_issue", "true", "Delivery status or delay issue"),
    57: ("general_support", "false", "General customer inquiry or complaint"),
    58: ("general_support", "false", "General customer inquiry or complaint"),
    59: ("general_support", "false", "General customer inquiry or complaint"),
    60: ("general_support", "false", "General customer inquiry or complaint"),
    61: ("general_support", "false", "General customer inquiry or complaint"),
    62: ("delivery_issue", "false", "Delivery status or delay issue"),
    63: ("general_support", "true", "General customer inquiry or complaint"),
    64: ("prime_subscription", "true", "Prime subscription inquiry"),
    65: ("general_support", "false", "General customer inquiry or complaint"),
    66: ("general_support", "false", "General customer inquiry or complaint"),
    67: ("general_support", "false", "General customer inquiry or complaint"),
    68: ("delivery_issue", "false", "Delivery status or delay issue"),
    69: ("delivery_issue", "true", "Delivery status or delay issue"),
    70: ("payment_billing", "false", "Payment or billing issue"),
    71: ("general_support", "true", "General customer inquiry or complaint"),
    72: ("prime_subscription", "true", "Prime subscription inquiry"),
    73: ("delivery_issue", "false", "Delivery status or delay issue"),
    74: ("general_support", "false", "General customer inquiry or complaint"),
    75: ("order_issue", "true", "Order placement or management issue"),
    76: ("general_support", "false", "General customer inquiry or complaint"),
    77: ("delivery_issue", "false", "Delivery status or delay issue"),
    78: ("general_support", "false", "General customer inquiry or complaint"),
    79: ("delivery_issue", "false", "Delivery status or delay issue"),
    80: ("delivery_issue", "false", "Delivery status or delay issue"),
    81: ("general_support", "false", "General customer inquiry or complaint"),
    82: ("general_support", "false", "General customer inquiry or complaint"),
    83: ("general_support", "false", "General customer inquiry or complaint"),
    84: ("order_issue", "false", "Order placement or management issue"),
    85: ("general_support", "false", "General customer inquiry or complaint"),
    86: ("general_support", "false", "General customer inquiry or complaint"),
    87: ("delivery_issue", "false", "Delivery status or delay issue"),
    88: ("delivery_issue", "false", "Delivery status or delay issue"),
    89: ("general_support", "false", "General customer inquiry or complaint"),
    90: ("delivery_issue", "false", "Delivery status or delay issue"),
    91: ("delivery_issue", "false", "Delivery status or delay issue"),
    92: ("general_support", "true", "General customer inquiry or complaint"),
    93: ("general_support", "false", "General customer inquiry or complaint"),
    94: ("general_support", "false", "General customer inquiry or complaint"),
    95: ("general_support", "false", "General customer inquiry or complaint"),
    96: ("general_support", "false", "General customer inquiry or complaint"),
    97: ("general_support", "true", "General customer inquiry or complaint"),
    98: ("payment_billing", "true", "Payment or billing issue"),
    99: ("delivery_issue", "true", "Delivery status or delay issue"),
    100: ("general_support", "true", "General customer inquiry or complaint"),
    101: ("delivery_issue", "false", "Delivery status or delay issue"),
    102: ("delivery_issue", "false", "Delivery status or delay issue"),
    103: ("order_issue", "false", "Order placement or management issue"),
    104: ("general_support", "false", "General customer inquiry or complaint"),
    105: ("general_support", "false", "General customer inquiry or complaint"),
    106: ("general_support", "false", "General customer inquiry or complaint"),
    107: ("general_support", "false", "General customer inquiry or complaint"),
    108: ("order_issue", "true", "Order placement or management issue"),
    109: ("delivery_issue", "false", "Delivery status or delay issue"),
    110: ("general_support", "false", "General customer inquiry or complaint"),
    111: ("payment_billing", "true", "Payment or billing issue"),
    112: ("general_support", "false", "General customer inquiry or complaint"),
    113: ("account_access", "true", "Account hold or access issue"),
    114: ("general_support", "false", "General customer inquiry or complaint"),
    115: ("general_support", "false", "General customer inquiry or complaint"),
    116: ("delivery_issue", "false", "Delivery status or delay issue"),
    117: ("order_issue", "true", "Order placement or management issue"),
    118: ("payment_billing", "false", "Payment or billing issue"),
    119: ("delivery_issue", "false", "Delivery status or delay issue"),
    120: ("general_support", "false", "General customer inquiry or complaint"),
    121: ("general_support", "false", "General customer inquiry or complaint"),
    122: ("product_issue", "false", "Physical product or device issue"),
    123: ("general_support", "true", "General customer inquiry or complaint"),
    124: ("return_refund", "true", "Refund or return request"),
    125: ("delivery_issue", "false", "Delivery status or delay issue"),
    126: ("general_support", "true", "General customer inquiry or complaint"),
    127: ("digital_content", "true", "Digital content or streaming issue"),
    128: ("general_support", "false", "General customer inquiry or complaint"),
    129: ("return_refund", "true", "Refund or return request"),
    130: ("delivery_issue", "false", "Delivery status or delay issue"),
    131: ("general_support", "false", "General customer inquiry or complaint"),
    132: ("delivery_issue", "false", "Delivery status or delay issue"),
    133: ("delivery_issue", "false", "Delivery status or delay issue"),
    134: ("general_support", "false", "General customer inquiry or complaint"),
    135: ("delivery_issue", "false", "Delivery status or delay issue"),
    136: ("delivery_issue", "false", "Delivery status or delay issue"),
    137: ("delivery_issue", "false", "Delivery status or delay issue"),
    138: ("payment_billing", "false", "Payment or billing issue"),
    139: ("general_support", "true", "General customer inquiry or complaint"),
    140: ("delivery_issue", "true", "Delivery status or delay issue"),
    141: ("delivery_issue", "false", "Delivery status or delay issue"),
    142: ("delivery_issue", "false", "Delivery status or delay issue"),
    143: ("digital_content", "false", "Digital content or streaming issue"),
    144: ("digital_content", "true", "Digital content or streaming issue"),
    145: ("product_issue", "false", "Physical product or device issue"),
    146: ("delivery_issue", "true", "Delivery status or delay issue"),
    147: ("delivery_issue", "true", "Delivery status or delay issue"),
    148: ("order_issue", "false", "Order placement or management issue"),
    149: ("delivery_issue", "true", "Delivery delay or lost shipment"),
    150: ("return_refund", "true", "Refund or return request"),
    151: ("general_support", "false", "General customer inquiry or complaint"),
    152: ("product_issue", "false", "Physical product or device issue"),
    153: ("delivery_issue", "false", "Delivery status or delay issue"),
    154: ("delivery_issue", "true", "Delivery status or delay issue"),
    155: ("general_support", "true", "General customer inquiry or complaint"),
    156: ("return_refund", "true", "Refund or return request"),
    157: ("account_access", "true", "Account hold or access issue"),
    158: ("general_support", "false", "General customer inquiry or complaint"),
    159: ("order_issue", "true", "Order placement or management issue"),
    160: ("prime_subscription", "false", "Prime subscription inquiry"),
    161: ("payment_billing", "false", "Payment or billing issue"),
    162: ("payment_billing", "false", "Payment or billing issue"),
    163: ("delivery_issue", "true", "Delivery status or delay issue"),
    164: ("payment_billing", "false", "Payment or billing issue"),
    165: ("order_issue", "false", "Order placement or management issue"),
    166: ("general_support", "false", "General customer inquiry or complaint"),
    167: ("payment_billing", "false", "Payment or billing issue"),
    168: ("order_issue", "false", "Order placement or management issue"),
    169: ("general_support", "false", "General customer inquiry or complaint"),
    170: ("delivery_issue", "false", "Delivery status or delay issue"),
    171: ("delivery_issue", "false", "Delivery status or delay issue"),
    172: ("delivery_issue", "false", "Delivery status or delay issue"),
    173: ("payment_billing", "false", "Payment or billing issue"),
    174: ("return_refund", "false", "Refund or return request"),
    175: ("general_support", "true", "General customer inquiry or complaint"),
    176: ("general_support", "false", "General customer inquiry or complaint"),
    177: ("delivery_issue", "false", "Delivery status or delay issue"),
    178: ("delivery_issue", "true", "Delivery status or delay issue"),
    179: ("general_support", "false", "General customer inquiry or complaint"),
    180: ("delivery_issue", "true", "Delivery status or delay issue"),
    181: ("delivery_issue", "false", "Delivery status or delay issue"),
    182: ("general_support", "true", "General customer inquiry or complaint"),
    183: ("product_issue", "false", "Physical product or device issue"),
    184: ("general_support", "true", "General customer inquiry or complaint"),
    185: ("delivery_issue", "false", "Delivery status or delay issue"),
    186: ("delivery_issue", "false", "Delivery status or delay issue"),
    187: ("general_support", "false", "General customer inquiry or complaint"),
    188: ("delivery_issue", "false", "Delivery status or delay issue"),
    189: ("general_support", "true", "General customer inquiry or complaint"),
    190: ("return_refund", "true", "Refund or return request"),
    191: ("delivery_issue", "false", "Delivery status or delay issue"),
    192: ("order_issue", "false", "Order placement or management issue"),
    193: ("digital_content", "false", "Digital content or streaming issue"),
    194: ("delivery_issue", "false", "Delivery status or delay issue"),
    195: ("delivery_issue", "false", "Delivery status or delay issue"),
    196: ("general_support", "true", "General customer inquiry or complaint"),
    197: ("delivery_issue", "true", "Delivery status or delay issue"),
    198: ("order_issue", "false", "Order placement or management issue"),
    199: ("general_support", "false", "General customer inquiry or complaint"),
}


def complete_and_validate_golden_set():
    print("Loading golden set from:", GOLDEN_PATH)
    if not GOLDEN_PATH.exists():
        raise FileNotFoundError(f"Golden set file not found at {GOLDEN_PATH}")

    # Read dataset
    df = pd.read_csv(GOLDEN_PATH)

    # 1. Validate Row Count
    if len(df) != SAMPLE_SIZE:
        raise ValueError(f"Expected exactly {SAMPLE_SIZE} rows, found {len(df)}")

    # 2. Validate Locked Intent Taxonomy
    valid_intents = set(get_intent_names())

    # 3. Preserve original text & tweet IDs for integrity check
    orig_customer_text = df["customer_text"].copy()
    orig_agent_response = df["agent_response"].copy()
    orig_tweet_id_cust = df["tweet_id_customer"].copy()
    orig_tweet_id_reply = df["tweet_id_reply"].copy()

    # Populate fields
    for idx, (intent, escalate, notes) in GOLDEN_ANNOTATIONS.items():
        if intent not in valid_intents:
            raise ValueError(f"Row {idx}: Invalid intent '{intent}' not in locked taxonomy")
        
        df.at[idx, "gold_intent"] = intent
        df.at[idx, "gold_escalate"] = str(escalate).lower()
        df.at[idx, "label_notes"] = notes

    # Integrity Assertions
    if not df["customer_text"].equals(orig_customer_text):
        raise ValueError("CRITICAL: customer_text was modified!")
    if not df["agent_response"].equals(orig_agent_response):
        raise ValueError("CRITICAL: agent_response was modified!")
    if not df["tweet_id_customer"].equals(orig_tweet_id_cust):
        raise ValueError("CRITICAL: tweet_id_customer was modified!")
    if not df["tweet_id_reply"].equals(orig_tweet_id_reply):
        raise ValueError("CRITICAL: tweet_id_reply was modified!")

    # Check for missing values
    missing_intents = df["gold_intent"].isna() | (df["gold_intent"] == "")
    missing_escalate = df["gold_escalate"].isna() | (df["gold_escalate"] == "")
    missing_notes = df["label_notes"].isna() | (df["label_notes"] == "")

    if missing_intents.any():
        raise ValueError(f"Found {missing_intents.sum()} rows with missing gold_intent")
    if missing_escalate.any():
        raise ValueError(f"Found {missing_escalate.sum()} rows with missing gold_escalate")
    if missing_notes.any():
        raise ValueError(f"Found {missing_notes.sum()} rows with missing label_notes")

    # Check duplicate tweet pairs
    duplicate_pairs = df.duplicated(subset=["tweet_id_customer", "tweet_id_reply"]).sum()
    if duplicate_pairs > 0:
        raise ValueError(f"Found {duplicate_pairs} duplicate tweet ID pairs")

    # Save output
    df.to_csv(GOLDEN_PATH, index=False)
    print(f"Successfully saved completed golden set to {GOLDEN_PATH}\n")

    # Print Validation Summary
    print("Golden set validation")
    print("---------------------")
    print(f"Rows: {len(df)}")
    print(f"Intent labels: {len(df) - missing_intents.sum()}/{len(df)}")
    print(f"Escalation labels: {len(df) - missing_escalate.sum()}/{len(df)}")
    print(f"Notes: {len(df) - missing_notes.sum()}/{len(df)}")
    print(f"Invalid intents: 0")
    print(f"Duplicate pairs: {duplicate_pairs}")

    print("\nIntent distribution:")
    intent_dist = df["gold_intent"].value_counts()
    for intent, count in intent_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {intent:20s}: {count:3d} ({percentage:5.1f}%)")

    print("\nEscalation distribution:")
    esc_dist = df["gold_escalate"].value_counts()
    for esc_val, count in esc_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {esc_val:20s}: {count:3d} ({percentage:5.1f}%)")


if __name__ == "__main__":
    complete_and_validate_golden_set()
