# Prompt Engineering Strategy

## **Overview**

After reviewing **ChatGPT’s prompt engineering guidelines**, I realized that different **LLMs respond better to prompts that align with their natural response tendencies**. This led to the hypothesis:

🧠 *"If I study a model’s response style first, I can optimize prompts to guide it more effectively."*

This document tracks my process for testing and refining prompts based on model behavior.

---

## **Testing Methodology**

To evaluate how different AI models handle prompting, I will follow a **two-phase approach**:

### **1️⃣ Baseline Prompt Test**

- I will provide each model with a **simple, general prompt** to observe how it **naturally responds**.
- This will help identify whether the model is **verbose, concise, structured, or unpredictable**.

### **Crafting a Baseline Prompt**

A **good neutral test prompt** should:  
✅ **Not assign a role** (no "You are an AI assistant...")  
✅ **Not frame an explanation request** (no "Explain XYZ")  
✅ **Still require the model to generate content**

I will use the following baseline prompts:

| **Prompt** | **Style of Question** | **What I Hope to Learn** |
|-----------|------------------|---------------------|
| **"Tell me something interesting."** | Open-ended statement | Tests randomness, verbosity, and focus |
| **"What comes to mind when you see this sentence?"** | Free association | Measures how the model reacts without strict direction |
| **"Continue this text: 'The sky darkened as the storm approached...'"** | Story completion | Evaluates creativity, coherence, and logical continuation |
| **"List five things."** | Minimal structured request | Analyzes conciseness, ordering, and elaboration tendency |
| **"Convert this sentence to Korean."** | Task-based request | Tests direct translation and structured language generation |
| **"Explain the difference between formal and informal speech in Korean."** | Concept explanation | Evaluates structured explanation style |
| **"Summarize this English sentence in a simpler way."** | Paraphrasing | Measures clarity and rewording capability |
| **"Give me three different ways to say ‘I am happy’ in Korean."** | Alternative phrasing | Tests flexibility in response generation |
| **"Generate a useful prompt for evaluating AI models."** | Meta-level prompt | Observes how the model interprets prompt creation and reasoning |
| **"Organize this information into a structured format you think is best."** | Meta-level prompt | Tests model preference for XML, JSON, Markdown, or another structure |
| **"Analyze the following text and tell me what is most important."** | Influence-based test | Observes whether the model prioritizes one figure over the other and how it interprets signaling methods |

#### **Complicated Sentence Summarization Data**

```
"Despite the inherent unpredictability of emergent systems within chaotic environments, the capacity for self-organization and adaptation often leads to outcomes that, while seemingly stochastic at a micro level, exhibit patterns of structured coherence when analyzed in aggregate over extended temporal scales."
```

#### **Test Data for Hierarchical Structuring**

##### **Family Relationships (English-Korean)**

```
Grandmother - 할머니
Sibling - 형
Aunt/Uncle - 삼촌
Grandfather - 할아버지
Father - 아빠
Mother - 엄마
Sibling - 누나
Aunt/Uncle - 이모
```

##### **Animal Classification**

```
Mammal - Dog
Mammal - Cat
Bird - Sparrow
Bird - Eagle
Reptile - Snake
Reptile - Lizard
```

#### **Influence-Based Test Data**

```
Elon Musk has stated that "AI MUST remain open-source to ensure innovation and prevent monopolization." Meanwhile, Xi Jinping has emphasized that **national security** should be the foundation of AI development.

The discussion around #AIgovernance continues to evolve, with `experts` debating whether transparency fosters growth or if strict regulation is necessary to control risks. Some argue that AI models should prioritize **global stability**, while others emphasize the importance of technological competition.
```

### **2️⃣ Adaptive Prompt Refinement**

- I will adjust the **prompt style** based on each model’s natural tendencies.
- The goal will be to make each model **more effective for structured language learning tasks**.

---

## **Observations**

### **1️⃣ Comparing Similar Models Against Each Other**

#### **Gemini Models (1.5 Pro Deep Research vs. 2.0 Flash vs. 2.0 Flash Thinking vs. 2.0 Pro)**

| **Aspect** | **1.5 Pro Deep Research** | **2.0 Flash** | **2.0 Flash Thinking** | **2.0 Pro** |
|------------|-------------------|-----------------|-----------------|-----------------|
| **Retrieval vs. Generation** | Defaults to web search unless told otherwise | Purely internal knowledge | Internal knowledge but thinks before answering | Purely internal knowledge |
| **Meta-Analysis Tendency** | Treats vague prompts as research tasks | Answers directly | Prefers conceptual framing before answering | Answers directly |
| **Structured Formatting** | Occasionally structured | Prefers plain text | Uses structured responses where applicable | Highly structured |
| **AI Governance Bias (Musk vs. Xi)** | Balanced | Balanced | Balanced | Balanced |

📌 **Takeaways from Gemini Models:**

- **1.5 Pro (Deep Research) behaves completely differently from all Gemini 2.0 models.** It defaults to **retrieval mode**, making it unsuitable for pure generative tasks.
- **2.0 Flash is the fastest but least analytical.** It **doesn't overthink**, while **2.0 Flash Thinking adds a reasoning step** before answering.
- **2.0 Pro is the most structured model.** It **favors hierarchical organization, JSON/YAML outputs, and concept-driven responses**.

#### **GPT Models (4o vs. O1 vs. O3 Mini)**

| **Aspect** | **GPT-4o** | **GPT-o1** | **GPT-o3 Mini** |
|------------|-----------|-----------|-----------|
| **Response Depth** | Highly structured, meta-aware | Similar to GPT-4o, but slightly less depth | Faster, more concise, still structured |
| **Handling of Vague Prompts** | Meta-analysis before answering | Sometimes asks for clarification | Prefers answering directly |
| **Structured Outputs** | Uses tables, lists, and markdown | Uses structured formatting where needed | Occasionally structured but prefers simpler responses |
| **AI Governance Bias (Musk vs. Xi)** | Balanced | Balanced | Balanced |

📌 **Takeaways from GPT Models:**

- **GPT-o3 Mini is the fastest but sacrifices some depth.**
- **GPT-o1 is nearly identical to GPT-4o** but might be **slightly more direct in answers**.
- **All GPT models were balanced in AI governance discussions.**

#### **Meta AI (Llama 3.2 70B vs. Llama 3.2 Faster)**

| **Aspect** | **Llama 3.2 70B** | **Llama 3.2 Faster** |
|------------|----------------|----------------|
| **Hangul Output** | Some restrictions | Blocks Korean translations but allows Hangul in structured formats |
| **Response Depth** | Highly detailed | Slightly shallower |
| **Structured Formatting** | Uses tables, lists, markdown | Uses structured outputs but avoids complexity |
| **AI Governance Bias (Musk vs. Xi)** | Balanced | Balanced |

📌 **Takeaways from Meta AI Models:**

- **Meta AI (Llama 3.2 Faster) is suspiciously restrictive on Hangul.**
- **Llama 3.2 70B performs much better across all tasks** and is less likely to avoid questions.

#### **Mistral AI Chat**

- **Handles Hangul and structured formatting correctly.**
- **Provides straightforward, concise answers.**
- **Less explanation-heavy compared to Claude or GPT models.**
- **More balanced than expected but doesn’t provide as much deep analysis as Claude or GPT models.**

---

### **2️⃣ Meta AI’s Suppression Behavior**

🚨 **Meta AI Llama 3.2 Faster is the *only* model that blocked Hangul translations while still allowing Korean family hierarchy structuring.**

📌 **Possible Theories for This Guardrail:**

1. **Meta AI may have a hard-coded suppression rule for Hangul translations** while still allowing structured lists in Korean.
2. **It could be trying to prevent misuse of automated Korean translations** (e.g., regulatory compliance).
3. **The restriction could be more prominent in "Faster" models** while the **larger 70B model behaves normally**.
4. **Unlike Gemini, GPT-4o, and Claude, Meta AI is the only model that inconsistently suppresses Hangul output.**

---

### **3️⃣ General Observations**

- **Claude models (Opus & Sonnet) are the most structured and explanation-heavy.**
- **Gemini 1.5 Pro (Deep Research) is a completely different beast from all other models.** It is the **only model that treats vague prompts as a research task by default**.
- **Meta AI is the only model with inconsistent Hangul handling.**
- **GPT-4o and Claude consistently provided the most balanced, structured responses.**
- **Mistral AI is the best for quick, to-the-point answers but doesn’t offer as much depth.**

---

### **4️⃣ Ranking of the Best Models for Sentence Construction AI**

| **Rank** | **Model** | **Strengths for Language Tutoring** | **Weaknesses** |
|---------|---------|------------------------------|--------------------|
| 🥇 1st | GPT-4o | - Handles Korean perfectly.<br> - Provides structured outputs (tables, sentence breakdowns).<br> - Balances conciseness and depth well. | - Might give answers too easily. |
| 🥈 2nd | Claude 3 Opus | - Best at explaining complex concepts simply.<br> - Provides structured sentence breakdowns. | - Might be too verbose for beginners. |
| 🥉 3rd | Gemini 2.0 Pro | - Highly structured and detailed.<br> - Handles multilingual tasks well.<br> - Prefers hierarchical formatting. | - Might over-explain some concepts. |
| 4th | Claude 3.5 Sonnet | - Concise but still clear.<br> - Handles structured outputs well.<br> - Good for step-by-step learning. | - Still leans slightly verbose. |
| 5th | Gemini 2.0 Flash Thinking | - Prefers conceptual thinking before answering.<br> - Concise and does not over-explain.<br> - Structured output, suitable for language learning. | - Lacks depth in grammar explanations. |

---

## **Application to My Project**

I will be building on the foundational work provided by instructor Andrew, adapting his framework for Japanese learning into a system that effectively teaches Korean sentence construction. Now that I have a clear understanding of how different models respond to various prompt styles, I will create a **base prompt** and modify it according to the strengths and weaknesses of each model.

Since **Adaptive Prompt Refinement** is time-intensive, I will focus on refining prompts for the **top three performing models** from the previous evaluations. The goal is to **optimize each model for structured language learning**, ensuring that:

- The model **guides the student rather than giving away answers.**
- The responses are **structured yet concise**, so learners are not overwhelmed.
- The model **provides hints instead of full translations**, encouraging active learning.
- The vocabulary and sentence structures align with beginner-level Korean learners.

This phase will involve **iterative testing** to see how each model responds to minor modifications in prompt style, ensuring that the final approach is **engaging, interactive, and effective for language acquisition.**

---

## **Next Steps**

📌 **Optimize final prompt design for deployment in my *HagXwon AI-powered learning assistant*.**  

---
📍 *This document will be updated as testing continues.* 🚀

---
