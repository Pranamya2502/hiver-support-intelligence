Decision Log

This log records non-obvious engineering and evaluation decisions made during the project.

D1. Selected AmazonHelp as the target brand

Decision: Use AmazonHelp as the single support brand.

Why: AmazonHelp had high support-response volume, strong customer-to-brand reply linkage, diverse support issues, and enough historical responses to make retrieval useful.

Trade-off: The system is specialized to one brand rather than being a generic multi-brand support agent.

D2. Built customer-agent pairs from reply relationships

Decision: Construct the working dataset from inbound customer tweets paired with AmazonHelp outbound replies using the dataset's reply/thread relationships.

Why: The assignment requires grounding replies in how the brand historically resolved similar issues. A paired customer message + historical agent response is therefore more useful than treating tweets independently.

Trade-off: Some conversational context outside the paired messages is lost.

D3. Used a small 9-intent taxonomy

Decision: Define nine broad support intents instead of many fine-grained classes.

Why: Fine-grained categories would increase ambiguity and make reliable classification harder, especially with noisy social-media messages.

Trade-off: Some distinct issues are grouped into the same broad category.

D4. Created a 200-example hand-labelled golden set

Decision: Use 200 manually labelled examples for evaluation.

Why: The assignment requires a hand-labelled golden set between 150 and 250 examples. A fixed 200-example set gives enough coverage while keeping manual annotation practical.

Trade-off: 200 examples are useful for prototype evaluation but are not large enough to represent production performance.

D5. Used a fixed random seed for golden-set sampling

Decision: Sample the golden set with random seed 42.

Why: A deterministic sample makes the evaluation reproducible and prevents the benchmark from changing between runs.

Trade-off: The chosen sample may not perfectly represent the full dataset.

D6. Used Sentence Transformers + FAISS for retrieval

Decision: Use sentence-transformers/all-MiniLM-L6-v2 embeddings with FAISS IndexFlatIP.

Why: Semantic embeddings handle paraphrases better than exact keyword matching, while FAISS provides a simple and fast vector-search implementation.

Trade-off: Building the full index is computationally heavier than a simple lexical retrieval system.

D7. Used normalized inner-product search for cosine similarity

Decision: L2-normalize embeddings and use FAISS inner-product search.

Why: After normalization, inner product is equivalent to cosine similarity. This gives an exact and easy-to-interpret similarity score.

Trade-off: IndexFlatIP is an exact search index and therefore requires more computation than approximate nearest-neighbour indexes at larger scale.

D8. Retrieve top-5 historical examples

Decision: Retrieve the top five historical conversations for each incoming message.

Why: One example can be misleading, while too many examples add unnecessary context and noise. Top-5 provides a small evidence set for grounded response generation.

Trade-off: The best answer may sometimes be outside the top five retrieved examples.

D9. Separated escalation logic from the LLM

Decision: Make the auto-handle/escalate decision using explicit rules instead of asking the LLM to freely decide.

Why: Escalation is a safety-sensitive product decision. Explicit thresholds make the behavior deterministic, inspectable, and easier to tune.

Current thresholds:

Intent confidence >= 0.75

Best historical evidence similarity >= 0.65

Trade-off: Fixed thresholds may not be optimal until confidence calibration is performed.

D10. Added a traditional TF-IDF baseline

Decision: Compare the AI classifier against TF-IDF + Logistic Regression.

Why: A strong classical baseline is useful for determining whether the LLM-based approach actually adds value beyond standard supervised text classification.

Trade-off: The baseline does not use historical retrieval or generative response capabilities.

D11. Added a nearest historical-response reply baseline

Decision: Use the response associated with the single most similar historical customer message as a simple reply baseline.

Why: This provides a direct comparison for whether generated replies are preferable to simply reusing a historical support response.

Important limitation: The golden examples were sampled from the same historical corpus used for retrieval. Therefore, exact historical matches can occur.

Consequence: This baseline is treated as a reference point, not an independent production-quality benchmark.

D12. Reported Macro-F1 in addition to accuracy

Decision: Report both intent accuracy and Macro-F1.

Why: The golden set is highly imbalanced, with general_support and delivery_issue representing a large share of the examples. Accuracy alone could hide poor performance on smaller intents.

Trade-off: Macro-F1 can be sensitive to small classes with very few examples, so it is interpreted together with accuracy and class distribution.

D13. Made the LLM evaluation resumable

Decision: The evaluation harness stores successful results and skips already completed examples on subsequent runs.

Why: LLM provider token/rate limits can interrupt a long evaluation. Resumability avoids repeating successful calls and wasting tokens.

Trade-off: The final benchmark must distinguish between successful evaluation coverage and the requested 200-example golden set.

D14. Added an LLM-as-judge rubric

Decision: Evaluate generated replies using four dimensions: relevance, groundedness, helpfulness, and overall quality, each scored from 1–5.

Why: Exact-match or lexical metrics are poorly suited to support replies because multiple responses can be correct. A rubric-based judge provides structured qualitative evaluation.

Trade-off: LLM judges can disagree with humans, so human validation is included rather than treating the judge as ground truth.

D15. Included human validation of the judge

Decision: Compare a sample of LLM-judge assessments with human assessments.

Why: The assignment explicitly asks for evidence of judge-human agreement. This provides a check on whether the automated judge is measuring response quality consistently.

Trade-off: Human validation covers only a sample rather than the full evaluation set.

D16. Chose explicit disclosure over hiding evaluation limitations

Decision: Report provider-limited coverage, class imbalance, and retrieval/golden-set overlap in the final documentation.

Why: A single headline number can be misleading if the evaluation has incomplete coverage or benchmark leakage/overlap. Explicit disclosure makes the result easier to interpret.

Trade-off: The reported prototype results may appear less impressive, but they are more defensible and reproducible.