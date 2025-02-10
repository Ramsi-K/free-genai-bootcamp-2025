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

### **2️⃣ Adaptive Prompt Refinement**

- I will adjust the **prompt style** based on each model’s natural tendencies.
- The goal will be to make each model **more effective for structured language learning tasks**.

---

## **Observations**

Once I conduct the baseline tests and refine the prompts, I expect to observe patterns in how different models respond. I will track key aspects such as verbosity, structure, and adherence to instruction.

I will update this section with specific findings after the testing phase.

---

## **Application to My Project**

Since my **Sentence Constructor** project will rely on **structured, clear explanations for language learning**, I plan to update this section after testing to reflect the best strategies based on observed model behavior.

---

## **Next Steps**

📌 **Run baseline tests and document initial outputs.**  
📌 **Analyze differences in model responses and refine prompts.**  
📌 **Optimize final prompt design for deployment in my _HagXwon AI-powered learning assistant_.**  

---
📍 *This document will be updated as testing continues.* 🚀

---