Evaluation Report

1. Evaluation Objective

The evaluation measures whether the AI support agent can:

Correctly classify incoming customer messages into the defined support intents.

Make a reasonable auto-handle versus escalation decision.

Generate relevant, grounded, and helpful support replies.

Improve meaningfully over simple baselines.

The evaluation uses a manually labelled 200-example golden set created from AmazonHelp support conversations.

2. Evaluation Dataset

The golden set contains 200 examples with:

Customer message

Historical AmazonHelp response

Gold intent

Gold escalation decision

Label notes

The intent distribution is imbalanced:

Intent

Examples

general_support

81

delivery_issue

63

order_issue

15

payment_billing

13

return_refund

10

digital_content

7

product_issue

5

account_access

3

prime_subscription

3

Total

200

Because of this imbalance, both accuracy and Macro-F1 are reported.

3. Baselines

Majority-Class Baseline

The majority baseline always predicts the most frequent intent.

This establishes the minimum performance expected from a classifier that ignores the message content.

TF-IDF + Logistic Regression

A traditional supervised text-classification baseline was implemented using TF-IDF features followed by Logistic Regression.

This provides a useful comparison against a conventional machine-learning approach.

Nearest Historical-Response Baseline

For reply generation, the system retrieves the single most similar historical customer message and directly returns its associated AmazonHelp response.

This provides a simple retrieval-only reference for evaluating generated replies.

Important limitation: the golden examples were sampled from the same historical corpus used by the retriever. Therefore, exact historical matches can occur. The reported similarity for this baseline should not be interpreted as an independent held-out retrieval score.

4. Metrics

Intent Classification

Accuracy: fraction of examples with the correct predicted intent.

Macro-F1: average F1 across all intent classes, giving each class equal weight.

Macro-F1 is particularly important here because the golden set contains many more general_support and delivery_issue examples than some of the smaller classes.

Escalation

The agent also reports escalation-decision accuracy.

The current escalation policy uses:

Intent confidence threshold: 0.75

Minimum historical evidence similarity: 0.65

Reply Quality

Generated replies are evaluated using an LLM-as-judge rubric:

Relevance: 1–5

Groundedness: 1–5

Helpfulness: 1–5

Overall quality: 1–5

A human validation sample is intended to measure agreement between the LLM judge and human assessment.

5. Results

The latest provider-limited run successfully completed 145 of the 200 AI-agent evaluations.

System

Intent Accuracy

Macro-F1

Majority baseline

40.50%

6.41%

TF-IDF + Logistic Regression

66.00%

49.19%

AI Agent*

58.62%

45.42%

Additional AI-agent results:

Metric

Result

Successful evaluations

145 / 200

Evaluation coverage

72.50%

Escalation accuracy

63.45%

API/run errors

55

Interpretation

The classical TF-IDF baseline currently outperforms the AI agent on intent classification in this partial run.

The AI agent achieves substantially better intent performance than the majority baseline, but it does not yet beat the supervised TF-IDF baseline.

This is useful evidence rather than a failure of the evaluation: the LLM-based approach should not automatically be assumed to outperform a simpler classifier.

The AI agent also provides capabilities that the TF-IDF classifier does not provide, including historical evidence retrieval, grounded response generation, and explicit escalation.

6. LLM Judge Results

The LLM judge was implemented with a fixed four-dimension rubric.

The current provider-limited judge run produced only 3 successful judgments because the same LLM-provider quota was reached during evaluation.

The available judge results are:

Criterion

Average Score

Relevance

4.33 / 5

Groundedness

5.00 / 5

Helpfulness

4.00 / 5

Overall

4.00 / 5

These values are not treated as final benchmark results because only three responses were successfully judged.

The evaluation harness can be rerun after the provider quota resets.

7. Top 5 Failure Cases

The failure analysis prioritizes cases with incorrect intent, incorrect escalation, and low model confidence.

Failure 1

Customer message:

@115850 https://t.co/JaLEb3OG0B

Gold intent: digital_content
Predicted intent: general_support
Gold escalation: No
Predicted escalation: Yes
Confidence: 0.50

Hypothesis: The message contains almost no semantic text and relies heavily on a URL/context that is not represented in the isolated message.

Failure 2

Customer message:

@AmazonHelp Amazon shipping.

Gold intent: delivery_issue
Predicted intent: general_support
Gold escalation: No
Predicted escalation: Yes
Confidence: 0.60

Hypothesis: The message is too short to clearly distinguish delivery from a generic shipping/support question.

Failure 3

Customer message:

Clients @115821 attention à l'arnaque qui tourne par mail !!! https://t.co/UgGWLuJjw1

Gold intent: delivery_issue
Predicted intent: general_support
Gold escalation: No
Predicted escalation: Yes
Confidence: 0.60

Hypothesis: The message contains multilingual text, a URL, mentions, and noisy social-media phrasing, making the intended support category difficult to infer from the isolated tweet.

Failure 4

Customer message:

@AmazonHelp No. it just diappears.

Gold intent: general_support
Predicted intent: order_issue
Gold escalation: No
Predicted escalation: Yes
Confidence: 0.65

Hypothesis: This is a context-dependent follow-up. Without the preceding conversation, the phrase can be interpreted as an order-related problem even though the gold label is general support.

Failure 5

Customer message:

@117086 EU TE VENEROOOOOO MEUS LIVROS JÁ CHEGARAM SCRR

Gold intent: general_support
Predicted intent: delivery_issue
Gold escalation: No
Predicted escalation: Yes
Confidence: 0.70

Hypothesis: Informal multilingual text and delivery-related vocabulary can cause the classifier to over-associate the message with delivery_issue.

8. Failure Patterns

Across the observed failures, four main patterns appear:

Very short messages provide insufficient semantic information.

Missing conversation context makes follow-up tweets difficult to classify.

Multilingual/noisy text reduces classification reliability.

Low confidence causes conservative escalation, reducing automation coverage.

These observations suggest that the next iteration should focus on context, multilingual robustness, and confidence calibration rather than simply increasing model complexity.

9. What Is Misleading About the Headline Number?

The AI Agent's current 58.62% intent accuracy should not be presented as a definitive production accuracy.

It is based on only 145 successful evaluations out of 200, because 55 LLM calls were blocked by the provider's daily token limit.

Other limitations are:

The golden set contains only 200 examples.

The intent distribution is highly imbalanced.

Several examples are extremely short or context-dependent.

The nearest-response baseline uses the same historical corpus from which the golden set was sampled, allowing exact matches.

Therefore, the current result is best described as a controlled prototype evaluation under provider-limited coverage, not a production performance estimate.

10. Judge-Human Agreement

The project includes a human-validation workflow for checking whether the LLM judge agrees with human assessment.

The human-validation file is:

reports/human_validation.csv

The validation schema includes:

Human relevance

Human groundedness

Human helpfulness

Human overall score

The current provider limitation resulted in only three successful LLM-judge examples, so a statistically meaningful judge-human agreement number is not claimed yet.

After the judge run is completed, the validation sample should be scored by a human and exact agreement / within-one agreement should be reported here.

11. Reproducibility

The evaluation is implemented as executable Python scripts.

Run the main evaluation:

python ml/evaluation/run_evaluation.py

Run the nearest-response baseline:

python ml/evaluation/nearest_response_baseline.py

Run the LLM judge:

python ml/evaluation/llm_judge.py

Prepare human validation and failure analysis:

python ml/evaluation/human_validation.py

The evaluation runner is resumable and preserves successful results, allowing interrupted LLM evaluations to continue without repeating completed calls.

12. Next-Week Plan

If given another week, I would prioritize:

Add conversation-level context for short follow-up messages.

Improve multilingual intent handling.

Calibrate confidence scores using human-labelled validation data.

Tune escalation thresholds using a validation split.

Evaluate retrieval against a held-out corpus to remove golden-set overlap.

Expand the golden set with harder and more balanced examples.

Measure latency and token cost for production-readiness analysis.

13. Final Takeaway

The prototype demonstrates an end-to-end support-agent workflow combining:

classification → historical retrieval → escalation → grounded response generation → evaluation

The current results also show an important engineering finding: the LLM-based classifier does not automatically outperform a simple TF-IDF baseline on this small, imbalanced golden set.

The strongest next step is therefore not to assume that a larger model will solve the problem, but to improve the evaluation design, add conversation context, calibrate uncertainty, and measure the quality of grounded responses separately from intent classification.