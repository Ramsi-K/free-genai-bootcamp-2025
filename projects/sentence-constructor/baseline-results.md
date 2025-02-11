# **Baseline Testing Results**

## **Test Setup**

- **[Baseline prompt](../docs/baseline-prompt.md)**
- **[Test sentences](../docs/baseline-tests.txt)**
- **Model responses:**
  - [GPT-4o](../docs/baseline-responses/gpt-4o.txt)
  - [Claude 3 Opus](../docs/baseline-responses/claude-3-opus.txt)
  - [Claude 3.5 Sonnet](../docs/baseline-responses/claude-3.5-sonnet.txt)

---

## **Model-Specific Feedback**

### **GPT-4o**

GPT-4o initially followed the structured approach, providing a vocabulary table, sentence structure, and hints without revealing the answer. However, after the student’s first attempt, it gave away the full correct translation instead of continuing with guided hints. It also over-explained alternative sentence forms too early, rather than letting the student figure out the correct conjugation. This violated the intended step-by-step learning process.

### **Claude 3 Opus**

Claude 3 Opus maintained the structured response format by first providing a vocabulary table and sentence structure before prompting the student to construct their own sentence. It gave clear, step-by-step feedback on student attempts, highlighting specific areas for improvement, such as missing particles or incorrect verb conjugation. Unlike some other models, it did not give away the full sentence outright but instead nudged the student toward the correct form through targeted corrections. However, one potential issue is that it provided multiple alternative sentence forms (casual, polite, formal) immediately after the correction, which might introduce unnecessary complexity for beginners. Overall, the model performed well in maintaining structured teaching but may need adjustments to limit excessive explanations when unnecessary.

### **Claude 3.5 Sonnet**

Claude 3.5 Sonnet successfully followed the structured approach by first providing a vocabulary table, sentence structure, and targeted hints without immediately revealing the answer. It effectively prompted the user to construct the sentence independently and provided incremental feedback based on student attempts rather than directly confirming correctness. However, as the conversation progressed, the model became more lenient in confirming correct responses and, in some cases, overly guided the student to the final answer rather than maintaining a fully interactive learning process. While it generally adhered to the structured hint-based approach, it occasionally validated incomplete attempts too quickly, reducing the opportunity for self-correction. The model also effectively handled word order corrections and spacing issues, ensuring that the student understood sentence construction at a fundamental level.

---

## **Testing Gemini 2.0 Pro with Gemini Gems**

I attempted to test **Gemini 2.0 Pro** using **Gemini Gems**, Google's experimental feature designed for multi-step AI interactions. However, this model does not currently support Gems, making it incompatible with the structured learning flow I needed. The only model that supports Gems is **Gemini 2.0**, which did not rank in my top 5 for sentence construction. As a result, I moved on to the next ranked model, **Claude 3.5 Sonnet**, to continue adaptive testing.

---

## **Comparison of Model Outputs Against Baseline Prompt**

Across all models, the initial responses closely followed the structured approach outlined in the **Baseline Prompt**. Each model began with a vocabulary table, sentence structure, and targeted hints instead of providing a direct translation. However, a common pattern emerged: models tended to **become increasingly lenient after two student attempts**. In most cases, if the student did not arrive at the correct answer within two responses, the AI would either confirm an incorrect attempt as "close enough" or fully reveal the correct sentence.

### **Additional Observations:**

- **Claude and GPT-4o maintained structured guidance slightly longer** before becoming lenient.
- **Gemini models provided excellent breakdowns initially** but tended to over-explain formality levels and variations after a correction.
- **Meta AI models exhibited inconsistent behavior,** especially with Hangul output, sometimes restricting translations.
- **Mistral AI, while concise, lacked depth in its explanations,** making it less suited for step-by-step correction.

### **Key Takeaways:**

This suggests that **most models operate under an implicit "two-attempt rule"** before defaulting to explicit instruction. Moving forward, prompt refinement should focus on **reinforcing hint-based progression across multiple student attempts** without prematurely revealing answers.
