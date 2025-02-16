# GenAI Bootcamp 2025 – Journal  

## Day 17: February 16, 2025  

I first **converted the provided Go-Gin backend specs to Python-Flask**, adapting everything for **Korean language learning**. I didn’t build directly from Go-Gin because I **don’t know Go at all**, but I do know Python—even though I’ve never worked with Flask before. I figured **debugging Python errors** would be easier than dealing with **Go from scratch**, and it worked. By **breaking down the issues step by step**, I was able to fully implement the backend in **Flask before rebuilding it in Go-Gin**. In hindsight, trying to build from the **original Go-Gin specs** would have been a nightmare. By breaking it down into a structured approach, **Cursor AI was able to guide the entire process effectively**, even though I had no prior Go experience.  

The setup took forever. Fixing database migrations, dependencies, and Go’s quirks (CGO, SQLite, GCC, environment paths) was exhausting. The biggest challenge was getting **make, GCC, and Go to work in the same environment**, but after multiple failed setups across **Windows, WSL, and MSYS2**, I finally got everything running. Once the backend was fully implemented, **testing became another battle**. The test cases were failing because of **duplicate data inserts and pagination mismatches**, which meant rewriting how test databases were structured. After several debugging rounds, all the tests finally passed, confirming that **the Go-Gin backend is fully functional**.  

**Completed Work**  

- **Converted AZW3 vocabulary book to JSON.**  
- **Converted Go-Gin backend specs to Python-Flask (Korean).**  
- **Fully implemented Flask before rebuilding in Go-Gin.**  
- **Fixed CGO, SQLite, GCC, and Make integration issues.**  
- **Successfully ran database migrations.**  
- **Debugged and passed all backend tests.**  

At this point, **both the Flask and Go-Gin backends are fully implemented and tested**. Next, I need to decide between **frontend integration or OPEA**.  

## Day 16: February 14, 2025  

I spent most of the day trying to set up an **AI-assisted backend case study** to compare how different LLMs generate Flask API code. The goal was to structure an experiment that tracked how tools like **Copilot, Windsurf, and Cursor** handled backend tasks. But after hours of planning, I realized the setup was too complicated, and I wasn’t getting the results I needed. Ultimately, I dropped the idea.  

Because of this, I didn’t watch any more of the backend lecture videos, and I didn’t write any code today.  

**Completed Work**

- **Planned an AI-assisted backend coding case study** (but scrapped it).  
- **Reviewed different prompting strategies for AI coding tools.**  

## Day 15: February 13, 2025  

Today was about **finalizing my backend understanding and preparing for implementation.** I wanted to start coding, but I needed to make sure I wasn’t going in blind.  

I started by **double-checking the missing API endpoints** that need to be implemented. There was some confusion about whether the homework was fully defined, so I spent time confirming that **the official documentation was incomplete** and that the real requirements were scattered across the livestreams and community discussions.  

Once I had clarity, I realized that I still needed a proper **plan for execution**. I reviewed the backend structure again—specifically **how Flask Blueprints handle routing**—and went over **how to connect the frontend to the backend** using API calls.  

At some point, I got sidetracked again when I found a **DRM restriction** on my Korean vocabulary book, which was frustrating because **it’s literally just a list of words, and I couldn’t even extract it properly.** This led me to look into **converting AZW3 files to TXT or JSON**, which ended up being way more annoying than expected. I tried multiple extraction methods, but nothing worked perfectly. Ultimately I was only able to copy over 200 words as the publisher has added copy restrictions on the book as well. I looked at other sources such as Anki and Quizlet and may end up using those instead.

Aside from that, I also thought more about my Level 5 project idea. The more I consider it, the more I realize I want **a visual-first language learning tool**, where flashcards use **images and videos instead of English translations**. I haven’t locked this in yet, but it’s definitely something I want to revisit once I finish the backend work.  

By the end of the day, I had a clearer **execution plan for finishing the backend**, and I know exactly what I need to do next.  

**Completed Work**  

- **Confirmed the actual API requirements** (tech specs vs. livestream corrections).  
- **Reviewed Flask Blueprints again** to make sure I understand how routing works.  
- **Figured out how the frontend will connect to the backend** (API calls, CORS setup).  
- **Tried to extract my Korean vocab book** but hit DRM restrictions.  
- **Revisited my Level 5 idea**—thinking about flashcards with AI-generated videos.  

## Day 14: February 12, 2025

I spent the entire day on backend work, research, and trying to make sense of everything. I started with the official lecture videos(6+ hrs), trying to wrap my head around the project requirements, Flask, SQLite, and how everything connects. At some point, I realized that there was no way I could do Level 5. I don’t know enough about frontend, backend, or anything full-stack. Even getting Level 1 done would be a huge achievement at this point.

Then I started thinking about Copilot and Cursor, since that is the entire project, and I realised that these tools offer drop down selections for different LLMs. That led me down a rabbit hole: which model is actually capable of coding, and in which languages does it return good quality code? I needed to know. So I ended up getting a bit sidetracked and wrote a nine-page research paper breaking it all down. I believed that this exploration would allow me to shoot for level 5 and grant the highest chance of success.

After that, I tried to get back to the backend videos, but I was still confused. I took the backend and frontend specs and turned them into diagrams, hoping that seeing everything visually would help. It did, but not completely. I still felt lost. Then I started breaking down the codebase, going file by file, and finally understood that the backend is using Flask Blueprints. That’s why there were no `@app.route()` functions in `app.py`, and why I was feeling lost.

I still have ~5 hours of lecture videos left, but I think I’ve cleared my head around the backend enough to start implementation tomorrow. I also know I’m done for the day because I’m getting snappy at my favorite AI assistant.

**Completed Work**

- Watched over six hours of backend lecture videos, covering Flask, SQLite, and API structures.  
- Realized that Level 5 is completely out of reach for me, and Level 1 is the real goal.  
- Wrote and published a nine-page research paper on LLM coding performance and model-language pairs.  
- Created multiple diagrams to visualize the backend structure and API interactions.  
- Broke down the codebase and figured out that the backend uses Flask Blueprints, finally making sense of how everything is structured.  

## Day 12 & 13: February 10-11, 2025

I pulled an all-nighter and have been working for over 10 hours straight because I was falling behind in the bootcamp. I'm exhausted. Submitting the Sentence Constructor project made me realize something critical—I’ve spent too much time on theory and note-taking and not enough on practical application. While I’m proud of my GenAI notes and thrilled to have learned TOGAF, I should have focused on getting the practical work done first, submitted it, and then refined the theory later. Moving forward, my plan is to prioritize completing the minimum requirements first, then improve upon them instead of getting lost in details upfront.

Completed Work:

- Finalized and submitted the Sentence Constructor Project, completing the README, technical uncertainties, refined prompt results, and full documentation.
- Tested and iterated prompts across multiple AI models, improving structured hinting, guided learning, and response enforcement.
- Identified key takeaways from testing: AI models have a two-attempt threshold, need predefined learning paths, and require progressive difficulty scaling to avoid large jumps in complexity.
- Completed the Technical Uncertainties document, summarizing challenges with AI-powered assistants, prompt portability, and integration into standalone systems.
- Created and refined the main project README, consolidating findings from baseline testing, refined prompt testing, and prompt engineering strategies.
- Cleaned up the repository structure, ensuring logical organization of prompts, results, and documentation.
- Submitted the bootcamp project form, finalizing hypotheses, technical exploration, and outcomes.

**Big Takeaway:**
I should have completed the practical requirements first and then refined the theory at my own pace. For the next week, my priority is execution—getting things done first and improving later. No more getting stuck in details. Time to adapt and move forward.

## Day 11: February 9, 2025

- **Finalized and committed the main repository README**, ensuring structured documentation across all projects.
- **Created the "Project Requirements" document** to define technical constraints, architectural goals, and implementation considerations.
- **Refined TOGAF compliance tracking and AI mapping**, ensuring enterprise architecture principles are integrated into the GenAI project.
- **Developed conceptual and high-level system diagrams** using **Mermaid and eraser.io**, aligning with TOGAF's ADM framework.
- **Structured and cleaned up business case and business proposal** for the AI-powered hagwon learning platform.
- **Started working on "Sentence Constructor" project**, focusing on **NLP-based AI guidance** for structured language learning.
- **Reviewed technical uncertainty and constraints for AI-powered assistants**, identifying key risks and prompting strategies.
- **Prepared for upcoming logical and physical architecture diagrams**, ensuring alignment with bootcamp submission deadlines.

## Day 10: February 8, 2025

- **Updated Main Repository README** to include a structured **directory overview**.
- **Added TOGAF Glossary** (`glossary.md`) documenting key TOGAF terms and definitions.
- **Created TOGAF Artifacts Document** (`togaf-artifacts.md`) listing inputs, outputs, and deliverables for each ADM phase.
- **Finalized TOGAF to AI Mapping Document** (`togaf-ai-mapping.md`) to align TOGAF enterprise architecture with AI workflows.
- **Added a README for the Notes Directory** (`notes/README.md`) to provide structured navigation of TOGAF, AI, and ML notes.
- **Worked on GenAI Architecting Project**, aligning AI architecture with **TOGAF principles**:
  - Defined **business goals and system structure**.
  - Outlined **requirements, risks, and assumptions**.
  - Roughly established **data strategy, model selection, and governance considerations**.
  - Structured key documentation for **technical architecture, implementation planning, and AI compliance**.

## Day 9: February 7, 2025

- Completed **TOGAF Module 3 Notes**, covering **Governance, Risk, and Techniques**.
- Refined understanding of **architecture compliance, risk management, and TOGAF techniques**.
- Attempted to create a **TOGAF Mindmap**, but found it too time-consuming and abandoned the idea.
- Went through the **ML Mini-Series by Rola Dali****, an instructor for the bootcamp. Created two sets of notes:
  - **Introduction to GenAI** notes, summarizing fundamental concepts.
  - **Architecting GenAI** notes, covering structured frameworks for designing AI-driven systems.
- Continued studying **Mid-Level and Low-Level System Design**, but found it **very confusing**.
- Tried different resources and explanations but still struggling to understand **LLD application and diagramming**.

## Day 8: February 5, 2025

- Completed **TOGAF Module 2 Notes**, breaking down **ADM phases** with **BIG Questions & Themes** for better clarity.
- Ensured structured understanding with a **WHO → WHAT → WHY → HOW → WHEN → NOW** approach.
- Improved readability and flow by refining transitions between phases.
- Watched refresher videos on **High-Level Design (HLD)** and **Low-Level Design (LLD)** for System Design.
- Worked on the **High-Level Architecture** as guided in the bootcamp tutorial.
- Struggled with **Mid-Level & Low-Level Design**, currently researching best practices and structured learning resources.
- Updated the **main README** to reflect **Korean Hagwon** instead of Japanese.

## Day 7: February 4, 2025

- Spent significant time researching **TOGAF** to gain a clearer understanding of enterprise architecture.
- Attempted to read the **official TOGAF documentation**, but found it dense and difficult to navigate.
- Engaged with **enterprise architecture professionals** on Discord and Reddit to seek advice on learning strategies.
- Based on recommendations, enrolled in a **Coursera TOGAF course** (free audit option).
- Completed **Module 1** of the course and took detailed notes in **Markdown format**.

## Day 6: February 3, 2025

- Developed a detailed **business scenario** for the HagXwon AI-powered language learning platform.
- Scoped out key **functional and business requirements**, ensuring alignment with real-world hagwon industry needs.
- Researched **TOGAF and enterprise architecture** principles to understand structured methodologies for large-scale AI implementation.
- Developed a **general understanding of TOGAF ADM framework** and how it applies to AI-powered education platforms.

## Day 5: February 1, 2025

- Expanded **BERT and fine-tuning** topics, covering **BERT, SBERT, and LoRA/RLHF techniques**.  
- Completed **Data and Machine Learning** notes, refining **ML pipelines, knowledge mining, and evaluation metrics**.  
- Finished **Prompt Engineering**, adding a **structured strategy table** and workflow for optimizing LLM outputs.  
- Fixed **Mermaid diagrams** to improve clarity and horizontal readability.  
- Prepared for next topics: **LLM Development Tools and Model Deployment Strategies**.  

## **Day 4: January 31, 2025**  

- Completed structured notes on **transformers, tokenization, and embeddings**, solidifying LLM fundamentals.  
- Created **Mermaid flowcharts** to visualize key NLP processes and architecture.  
- Refined **Week 00 README**, improving organization and linking correct note files.  
- Debugged **math rendering issues**, ensuring proper display of formulas.  
- Next focus: **BERT and fine-tuning techniques**.  

## **Day 3: January 30, 2025**  

- Completed detailed notes on **AI vs. Generative AI**, focusing on key differences, use cases, and impact.  
- Wrote structured documentation on **Large Language Models (LLMs)**, covering foundational models, embeddings, transformers, and real-world applications.  
- Refined **repo structure** to ensure clarity and scalability for upcoming weeks.  
- Fixed **Mermaid diagrams and math rendering issues**, ensuring all visuals are properly formatted.  
- Preparing for the next topic: **Tokenization & NLP fundamentals** in GenAI.  

## **Day 2: January 28, 2025**  

- Worked through **GenAI Essentials**, covering **AI vs. GenAI**, **LLMs**, and **transformers**.  
- Structured my **Week 00 folder**, adding separate **note files** for key topics.
- Created a **README for Week 00** summarizing key topics and indexing notes.  
- Ensured **repo structure is scalable** for future weeks of the bootcamp.  

## **Day 1: January 27, 2025**  

- Explored the **bootcamp structure, expectations, and requirements**.  
- Set up the **GitHub repository** and planned the **organization of notes and projects**.  
- Reviewed **GenAI Essentials course structure** and noted key topics to cover.  
- Started with **AI, ML, DL fundamentals**, understanding the relationship between traditional and generative AI.  
