Evaluation Report

Evaluation Objective

The evaluation measures whether the AI support agent can:

Correctly classify incoming customer messages into the defined support intents.

Make a reasonable auto-handle versus escalation decision.

Generate relevant, grounded, and helpful support replies.

Improve meaningfully over simple baselines.

The evaluation uses a manually labelled 200-example golden set created from AmazonHelp support conversations.

Evaluation Dataset

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

Baselines

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

Metrics

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

Results

The final evaluation successfully completed all 200 AI-agent evaluations with no API/run errors.

System

Intent Accuracy

Macro-F1

Majority baseline

40.50%

6.41%

TF-IDF + Logistic Regression

66.00%

49.19%

AI Agent

62.00%

51.69%

Additional AI-agent results:

Metric

Result

Successful evaluations

200 / 200

Evaluation coverage

100.00%

Escalation accuracy

61.50%

API/run errors

0

Interpretation

The classical TF-IDF baseline achieves higher raw intent accuracy than the AI agent (66.00% vs 62.00%), while the AI agent achieves higher Macro-F1 (51.69% vs 49.19%).

This shows that the AI agent is more balanced across the nine intent classes even though it has lower overall accuracy on this imbalanced golden set.

This is useful evidence rather than a failure of the evaluation: the LLM-based approach should not automatically be assumed to outperform a simpler classifier.

The AI agent also provides capabilities that the TF-IDF classifier does not provide, including historical evidence retrieval, grounded response generation, and explicit escalation.

LLM Judge Results

The LLM judge uses a fixed four-dimension rubric:

Relevance: 1–5

Groundedness: 1–5

Helpfulness: 1–5

Overall quality: 1–5

After the provider quota reset, the judge was rerun for the remaining responses. The latest run successfully produced 59 new judgments; previously completed judgments were preserved by the resumable judge workflow.

For the newly completed judge batch, the averages were:

Criterion

Average Score

Relevance

3.63 / 5

Groundedness

4.41 / 5

Helpfulness

3.54 / 5

Overall

3.49 / 5

These averages describe the newly successful judge batch rather than a clean 200-example aggregate, because the judge file was built incrementally across provider-limited runs. They should therefore be reported as a partial judge-quality result, not as a definitive 200-example benchmark.

Top 5 Failure Cases

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

Failure Patterns

Across the observed failures, four main patterns appear:

Very short messages provide insufficient semantic information.

Missing conversation context makes follow-up tweets difficult to classify.

Multilingual/noisy text reduces classification reliability.

Low confidence causes conservative escalation, reducing automation coverage.

These observations suggest that the next iteration should focus on context, multilingual robustness, and confidence calibration rather than simply increasing model complexity.

What Is Misleading About the Headline Number?

The AI Agent's 62.00% intent accuracy should not be presented as a definitive production accuracy.

The final AI evaluation covers all 200 golden examples, but the golden set is small and imbalanced.

Other limitations are:

The golden set contains only 200 examples.

The intent distribution is highly imbalanced.

Several examples are extremely short or context-dependent.

The nearest-response baseline uses the same historical corpus from which the golden set was sampled, allowing exact matches.

The LLM-judge averages are based on incrementally completed judge results rather than a clean, independently held-out 200-example judge sample.

Therefore, the result is best described as a controlled prototype evaluation, not a production performance estimate.

Judge-Human Agreement

The project includes a human-validation workflow for checking whether the LLM judge agrees with manual assessment.

The validation sample contains 20 examples and the following human scores:

Human relevance

Human groundedness

Human helpfulness

Human overall score

Exact agreement with the LLM judge on the reviewed sample was:

Relevance: 95%

Groundedness: 95%

Helpfulness: 100%

Overall: 80%

Average exact agreement across the four dimensions: 92.5%.

Within-one agreement was 100% across the reviewed dimensions.

This is a small validation sample, so it is evidence of judge consistency rather than a statistically definitive estimate of judge reliability.

Reproducibility

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

Next-Week Plan

If given another week, I would prioritize:

Add conversation-level context for short follow-up messages.

Improve multilingual intent handling.

Calibrate confidence scores using human-labelled validation data.

Tune escalation thresholds using a validation split.

Evaluate retrieval against a held-out corpus to remove golden-set overlap.

Expand the golden set with harder and more balanced examples.

Measure latency and token cost for production-readiness analysis.

Final Takeaway

The prototype demonstrates an end-to-end support-agent workflow combining:

classification → historical retrieval → escalation → grounded response generation → evaluation

The current results also show an important engineering finding: the LLM-based classifier does not automatically outperform a simple TF-IDF baseline on this small, imbalanced golden set.

The strongest next step is therefore not to assume that a larger model will solve the problem, but to improve the evaluation design, add conversation context, calibrate uncertainty, and measure the quality of grounded responses separately from intent classification.