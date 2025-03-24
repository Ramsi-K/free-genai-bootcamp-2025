<!---markdownlint-ignore MD012 MD036-->

# GenAI Bootcamp 2025 – Journal

## Jump to what I was doing in

- [Week 7](#week-7)
- [Week 6](#week-6)
- [Week 5 (Sick Week)](#week-5-sick-week)
- [Week 4](#week-4)
- [Week 3](#week-3)
- [Week 2](#week-2)
- [Week 1](#week-1)
- [Week 0](#week-0)
- [Pre-bootcamp](#pre-bootcamp-prep)

## Week 7

### Day 48: March 24, 2025

Today was a whirlwind of architecture, contemplation, and vibing through backend design. I finalized the outline for my next research paper: "Beyond Human Mimicry: Rethinking AI Identity in Generative Models." The structure includes seven core sections, each supported by real, recent citations. Topics covered include anthropomorphism, ethical realism vs. transparency, memory design, long-term interaction bias, and non-human AI identities. I also added a focused section on cultural variation with a spotlight on South Korea.

I officially kicked off backend development for the HagXwon project using FastAPI, building a working microservice-style flashcard system with GET and POST routes, real-time flashcard evaluation, and in-memory state tracking.

I extended this with sassy, emotionally-damaging tutor responses to simulate AhjummaGPT and began mentally structuring the full backend agent ecosystem. I mapped out use cases for multi-agent LLMs, including Flashcard Agent, Storybook Agent, MUD Game Agent, Listening Agent, and even a Live Object Detection Tutor using mobile camera input.

I explored fine-tuning strategies, LoRA, quantization tradeoffs, neuron depth and layer-wise behavior in LLMs, and the practicality of pruning out the “coding neurons” to create a strictly sass-based Korean tutor.

I created a Mermaid diagram of the full system and flowchart of execution for personality-injected, quantized LLMs. Also ideated the Noraebang Agent and revived the Song-to-Vocab pipeline as a potential Red League feature.

Although I only watched 7 minutes of the FastAPI video, I gained a full working understanding of core concepts by implementing everything manually and reverse-engineering the backend from scratch.

### Day 47: March 23, 2025

After finalizing Section 8 yesterday, I shifted into full production mode to close out the dissertation. I rewrote the conclusion and abstract, reviewed and reformatted the entire document, fixed spacing, updated figures, and checked fonts (yes, I switched to Times New Roman in the end). I exported the final version as a polished 100-page PDF and double all metadata, references, and citations. I also created a condensed version for LinkedIn, featuring selected diagrams and visuals. This included designing a custom title page, writing a visual summary, expanding on Korea as a testbed, and carefully refining tone, humor, and structure for broader appeal.

I published the full dissertation to Academia.edu and shared the PDF mini-paper on LinkedIn, Discord, and GitHub.

On GitHub, I added all three research projects — the LLM analysis, the Ouroboros paper, and the Turn Detection dissertation — under the `/research/` folder, each with its own markdown summary, links, and project structure update in the main `README.md`.

### Day 46: March 22, 2025

Today, I completed Section 8 of the dissertation, marking a major milestone in the project. This section: "Recent Advances, Notable Research, and Future Directions" -- was the most intensive by far. I re-read countless papers today, validating of every reference, integrating systems, and restructuring based on emerging themes. I merged and refined all previous drafts, verifying citation accuracy and consolidating some overlapping subsections. The final version includes advances in multimodal turn detection, cultural and neurodivergent adaptation, governance and privacy, unresolved challenges, and a set of forward-looking research directions. I also completed the Executive Summary, formally closing out the analytical portion of the paper. What remains now is the conclusion, back-revising the introduction and abstract, formatting the index, and preparing acknowledgements.

## Week 6

### Day 45: March 21, 2025

On this day, I finalized Section 7 of the paper, focusing on the ethical, social, and cultural considerations of AI-powered turn detection. This included in-depth discussions on bias, neurodivergence, accessibility, and regulatory frameworks, as well as the integration of the digital twin and identity theft argument to tie back to earlier privacy concerns. In addition to writing, I generated and refined a full set of visual aids for this section. I restructured and reworked the entirety of Section 8, to align better with the central theme of the paper as well as eliminating any redundancies from earlier sections. The new version is more in line with the rest of the paper now with a clear set of subsections: multimodal and cross-modal turn detection, adaptive cultural and linguistic systems, and neurodivergence-inclusive architectures. Further subsections on governance, real-time modeling, and research gaps are planned next. I also ran plagiarism checks on key sections and made necessary final edits to ensure originality and citation integrity. I hope to finish this tomorrow, I have to complete section 8, conclusion, final run through and any additional pages.

### Day 44: March 20, 2025

This was a major cleanup and structuring day. I finalized Sections 5 and 6 of the Turn Detection paper, refining case studies, eliminating redundancy, and integrating Korean-specific research (Lee & Kim, Oh & Min, etc.). I also ensured the technical details aligned with the main themes, adding necessary tables and comparisons where needed. Beyond that, I explored new ethical considerations in Section 7, particularly the risks of AI speech pattern retention and identity cloning, which unexpectedly ties into my Beyond Human Mimicry paper. The privacy implications of AI tutors mimicking user behaviors raised critical concerns about biometric data protection, deepfake fraud, and regulatory oversight. With these sections nearly locked in, my next steps are to verify Sections 5 & 6, refine Section 7's argument, and integrate further research on AI surveillance, biometric risks, and ethical forgetting models. It was a long but productive day, and the finish line is in sight.

### Day 43: March 19, 2025

Today was a high-output but mentally exhausting day. I made major progress on my Turn Detection Paper, integrating new research, refining structure, and ensuring consistency across sections. **Sections 1-4 are finalized**, with all visuals, tables, and citations properly placed. In Section 5, I restructured parts of the discussion to accommodate recent research on ASR/TTS advancements in AI tutoring, specifically for Korean learners (korean-to-english and english-to-korean) AI language learning applications, and adaptive strategies for neurodivergent users. While this strengthened the paper, it also made me rethink how to present this information without disrupting flow. I started reviewing Section 6, identifying inconsistencies in formatting, weak transitions, and redundant content, which will need further revision before moving forward.

On the **Agents** side, I revisited both my Agentic Story Builder and Code Assistance Agent projects, ensuring they still align with the bootcamp’s expectations for Week 3. I also revisited the Web Interaction Agent idea, considering how it could be extended to perform real-world actions instead of just retrieving information. While I reviewed the Hugging Face Agents course, I didn’t get into exercises yet. Something I'm still considering.

I also attended the Intel OPEA webinar on AgentsQnA. No live demo, but they presented pre-recorded videos of the system working, which makes me think that implementation might not be straightforward.

The biggest win of the day was a massive research breakthrough, finding multiple highly relevant papers on AI-driven language learning, ASR/TTS for Korean, and conversational AI for neurodivergent users. This reshaped how I'm structuring Section 5 and the overall research discussion.

At this point, I still feel like I have so much left to do. Section 6 needs final revisions, and I haven’t even touched Sections 7+ yet. On top of that, I still have bootcamp work for Weeks 3, 4, and 5, plus Agents Week tasks and the final integration.

### Day 42: March 18, 2025

Today, I focused primarily on debugging the OPEA megaservice, particularly the question-module implementation. I refined how questions are generated, ensuring they align with TOPIK-style assessments. I also investigated whether the system should generate questions based on video length or maintain a static question count.

While experimenting with different architectures, I initially separated the embedding and vector store services but later reintegrated them into the question module for better performance. I also built the main megaservice.py entry point and added a wrapper.py file to improve modularity. Unlike standard OPEA examples, my implementation takes a slightly different approach by testing whether services can remain more independent while still functioning within the megaservice architecture.

Additionally, I integrated telemetry using Prometheus and OpenTelemetry (OTEL) to track system performance and debugging data. Persistence was also added to ensure that generated questions and student scores are stored long-term. To visualize student progress, I developed a dashboard functionality that tracks total questions answered and correctness, allowing for a better assessment of learning outcomes.

Beyond debugging, I merged the latest updates from main into my listening-comp branch, ensuring everything remains up to date. I also (finally) started and finished watching the full 3-hour OPEA video, which provided necessary insights into telemetry and architecture best practices.

I also reviewed and planned the final touches for my Turn Detection paper which I will do first thing tomorrow. I briefly explored A-MEM which is a dynamic memory updating method that allows newer information to override old data without a full retraining. Broadly outlined the section for my Beyond Human mimicry paper with A-MEM and its parallels to human memory processes, including the potential for long-term bias accumulation akin to the StressPrompt effect.

### Day 41: March 17, 2025 (Sick Day)

- Watched **Tom Yeh’s Agents Course** lecture 1 and completed the associated homework as preliminary study for the upcoming Agents-focused assignments.
- Reviewed all career-focused videos on the GenAI Bootcamp page.

## Week 5 (Sick Week)

### Day 40: March 15, 2025

- Worked on recreating **"Munchers"** word game:
  - Inspired by Andrew’s office hours; played the original DOS version I found on Internet Archive.
  - Opted for **p5.js** instead of 3DJS for simplicity.
  - Completed a working prototype (standalone; no backend yet).
- Shared progress on the Bootcamp Discord. May integrate into the final MUD project later.

### Day 39: March 14, 2025

- Finished the first draft of my **Turn Detection** paper.
- Checked and verified references; awaiting Gemini’s review for factual accuracy, unsubstantiated claims, and missing citations.  
  _(Given the length (~60 pages), this might take a day or more.)_
- Abstract and final polishing still pending.

### Day 38: March 13, 2025

- Continued working on sections 6 and 7 of the **Turn Detection** paper, focusing on refining arguments and checking sources (**sections 6 and 7** completed).

### Day 36-37: March 11-12, 2025

- Experimented extensively with a "storybook" concept:
  - Inspired by Andrew’s example from office hours (image generation for children's stories).
  - Prompt-engineered Gemini to consistently generate coherent children's stories with related 6-panel comic-strip style images.
  - Successfully obtained translated stories as well, resulting in high-quality outputs.
- Shared results on Bootcamp Discord; planning possible future integration with the final project.

_Rested extensively both days due to illness._

### Day 36-37: March 9-10, 2025

Spent both days working on my research paper: **Turn Detection in AI-Powered Conversations: Implications for Language Learning Applications**. Initially, I thought this would take a single day, but the depth of the topic required more time.

I covered **theoretical foundations**, including linguistic models of turn-taking, cultural variations, and computational approaches. Explored how **AI systems handle turn detection**, from **early rule-based methods** to **deep learning architectures** like **transformers and multimodal models**.

Dived into **challenges in real-world AI applications**, including false positives, latency issues, and ASR/TTS limitations. Analyzed **AI language tutors, customer service bots, and virtual assistants**, highlighting where turn detection impacts user experience.

I originally planned to use **Claude** extensively for drafting this paper, but it **makes up references and statistics**, which meant I had to **double-check everything manually**. Claude is also falsifying claims, for e.g., if a source only mentions that deep learning multimodal systems are a promising area of research Claude turns that into "deep learning multimodal systems **will** significantly reduce turn detection errors".
This has caused additional delays, as I needed to verify all claims, cross-reference sources, and ensure factual accuracy before including any information.

Right now, the paper is **still incomplete**, but I’ve structured most of it and documented key insights. Next steps include **finalizing case studies**, integrating **more benchmarks**, and **tying it back to language learning AI**. Planning to wrap it up soon.

## Week 4

### Day 35: March 8, 2025

Worked on the OPEA megaservice for the Listening Learning App. Made significant progress in setting up the megaservice structure with three microservices: **transcript-processor, question-module, and audio-module**. Each microservice is now integrated into a single system, feeding into the megaservice.

Spent additional time configuring **GPU acceleration for Docker**, ensuring that the entire system could leverage NVIDIA GPUs for faster processing. The setup was more complex than expected, but after debugging and adjusting configurations, I successfully got it running.

Currently debugging an issue with the **transcript-processor** service. The guardrails implementation is incorrectly flagging longer videos (e.g., 8 minutes) as "too short," preventing them from being processed. Investigating the logic behind the rate-limiting and guardrails checks to pinpoint the issue.

Next step is to fix the transcript-processor bug

### Day 34: March 6, 2025

Finished the relevant lectures for Listening learning app and spent the remainder of the day on frontend development from scratch. I used chatgpt, bolt, and then Claude and copilot.
Added a comprehensive test suite to improve stability.
Finalized frontend structure and added a comprehensive test suite to the project. Submitted week 1 form.

### Day 32-33: March 4-5, 2025

Caught up on the official lectures on OPEA implementations, megaservice, troubleshooting and the Listening Learning App.
Took detailed notes on service orchestration, AI model integration, and megaservice workflows.
I want to build a megaservice and spent time understanding how to make it work.

### Day 31: March 3, 2025

Focused on OPEA architecture, refining the structure of microservices and megaservices. Implemented the Ollama-based microservice for structured query generation.
Worked on the Vocab Importer, setting up a Flask app running on Docker and successfully connecting it to Ollama for generating grouped word responses.

### Day 30: March 2, 2025

- Continued working on OPEA microservices and megaservices, focusing on integrating different models with Ollama. Successfully configured multiple models to run within the same environment, improving flexibility for AI-powered language tasks.
- Completed and published the Ouroboros paper on LinkedIn, finalizing research on AI-assisted coding techniques and their implications for software development workflows.
- Worked on frontend development, finalizing the tech stack and starting the initial implementation. This marks a shift from backend-heavy work to a more balanced approach, ensuring both API and UI components are properly aligned.
- Made progress on transitioning the Vocab Importer into a megaservice, aiming for a more scalable and modular design. Encountered issues with vLLM integration, requiring further debugging before the system is fully functional.
- Mapped out a broader plan for handling multiple bootcamp projects within a megaservice architecture. Identified three major megaservices—Language Learning, Visual Learning, and Interactive Learning—each consolidating related projects to maximize efficiency. The Speech Recognition microservice remains separate due to its specialized functionality. Moving forward, this structure will guide how different components interact and scale.

## Week 3

### Day 28-29: February 28 - March 1 2025

I focused on documenting key backend, database, and containerization concepts as part of my bootcamp work. I structured my notes across three main areas.

- For backend development, I covered REST APIs, request-response structure, Flask routing, and deployment basics. I also documented best practices for secure API design and production deployment using Gunicorn/Uvicorn.
- For database management, I explored SQLite3 basics, SQLAlchemy ORM, and data migrations. I created ChromaDB-specific notes, including a real-world use case for AI-driven vocabulary retrieval, and compared vector databases like Pinecone, Qdrant, and Weaviate.
- For containers and Docker, I documented Docker fundamentals, how to write a Dockerfile for Flask, and container security best practices. I also explained Docker Compose for multi-container applications, covering networking and environment management.

This documentation will help in deploying my OPEA-integrated Flask backend, ensuring scalability, security, and AI-powered functionality.

### Day 26-27: February 26-27, 2025

Added notes on OPEA microservices and megaservices, including a deep dive into microservices architecture, performance optimizations, advanced communication protocols, and deployment strategies. Expanded documentation on OPEA ecosystem and alternatives, data flow patterns, and major challenges and best practices. Structured comparisons for microservices vs. megaservices and created an in-depth breakdown of megaservice architecture. Made minor edits across multiple sections to improve clarity and consistency.

### Day 25: February 25, 2025

Wrapped up the backend completely today: Go/Gin is done, tests are passing above the bootcamp threshold, and there’s nothing left to tweak. Finally. It took way longer than expected, but the experiment was worth it.

Spent time finalizing documentation—updated the backend README, Lang Portal README, and roadmap so everything reflects actual progress. Now it’s clear what’s done, what’s next, and what needs prioritization.

Started watching OPEA videos and taking short notes. The concepts look complex, but breaking it down should help before diving into implementation. The next focus is shifting to OPEA and the remaining bootcamp projects.

Not a heavy coding day, but a necessary one. Now, moving forward.

## Week 2

### Day 23-24: February 23-24, 2025

Final stretch of the Lang Portal backend. After weeks of AI-assisted development, the system was functional, with 100% of model tests and 75% of handler integration tests passing, enough to meet the bootcamp requirement. The remaining issues were all tied to study session and activity tracking:

- **Study session** relations were inconsistent (group_id missing, incorrect state tracking).
- **Quick stats** calculations were unreliable (progress tracking errors).
- **Sentence practice** validation was failing (exact/partial match mismatches).
- **Study session** integration tests weren’t returning expected values.

Tried fixing these, but each attempted solution broke something else. After hours of debugging AI-generated logic, it became clear that this backend wasn’t something I even understood. Every line of code had been written by an AI assistant, without manual research, external docs, or traditional debugging.

_Final decision:_ Leaving the last stable commit. No forced fixes, no artificial patches. The experiment is done. AI can accelerate coding, but it can’t replace deep system understanding.

### Day 22: February 22, 2025

Backend is fully up and running. All tables initialize correctly, and data is seeding independently. Curl tests confirmed that API endpoints are returning the correct outputs.

- Word and group model tests are passing.
- Backend data flow is stable.
- Still debugging integration tests. Out of 61 total tests, 19 are failing, most likely due to database reset issues. Need to ensure a full clean reset between test runs before finalizing.

### Day 21: February 21, 2025

Successfully implemented database seeding for the core 2000 words, ensuring English translations and example sentences are stored correctly. Resolved handler file errors and completed the separation of JSON files into two databases for distinct tasks.

Spent time debugging study sessions, study activity handling, and test utilities, ensuring smooth interaction with the backend. The word model was functioning correctly, but integrating the group model introduced new challenges; adjustments were made to maintain stability while keeping the data structured properly.

Next steps involve refining API interactions to ensure they work seamlessly with the newly seeded data.

### Day 20: February 20, 2025

Attempted to use **Windsurf for debugging** but abandoned it due to excessive renaming and unhelpful refactoring. Recovered the **last known good commit** to revert Windsurf’s changes. With **Cursor credits exhausted**, switched to **Gemini (chat mode) for debugging**, following Andrew’s suggestion that Gemini should be strong in Go since Google developed both. Debugged issues manually with AI assistance where needed.

**Observations:**

### Day 19: February 19, 2025

Spent 10+ hours trying to fix the Go backend, but it was a frustrating loop of errors, misconfigurations, and unexpected issues.

**Issues Faced:**

- API endpoints were misaligned with frontend specs.
- `word_groups.json` was not loading properly.
- The database was not resetting correctly, causing duplicate/missing data.
- Groups were not being linked correctly to words.
- Pagination was broken, doubling the total word count.
- Study activities were inconsistent, and some APIs didn't return expected data.
- Error handling was unreliable across endpoints.

**Attempts to Fix:**

- Tried multiple prompts to get AI assistance, but fixes kept breaking other parts.
- Verified JSON file loading and checked mappings.
- Investigated test failures but couldn't fully resolve database contamination.
- Considered a full rebuild instead of debugging endlessly.

**Outcome:**

💀 Got nowhere. The codebase is too messy—decided to create a new branch and start fresh rather than continue patching. Tomorrow, I'll focus on rebuilding the backend properly from the frontend + backend specs instead of fixing bad code.

**Lessons Learned:**

I've noticed that AI coding assistants often take you in circles—they apply quick fixes without fully understanding the deeper structural issues. I knew this, but I let it happen anyway, hoping for an easy path forward. Instead, I spent hours debugging patches that just introduced new problems. Sometimes, it's better to step back and rebuild from a solid foundation rather than trying to fix something that's fundamentally broken.

### Day 18: February 17, 2025

Today was a lighter day compared to yesterday's intense backend work. I finalized the **HagXwon logo**—both the **modern version and the color variations**—and I'm happy with how they turned out. I also spent time watching the backend testing video, and that's when I realized I **completely forgot to implement the dashboard.** That hit hard because I thought I was done with backend, and now I have to go back and add it.

Aside from that, I started drafting an **opinion piece on AI's Ouroboric Knowledge Loop** looking at how AI models are feeding off their own outputs and what that means for the future of knowledge generation. The piece isn't finished yet, but I spent some time researching and structuring my thoughts.

- AI-assisted coding is unreliable without proper IDE integration.
- Gemini was useful for debugging but lacked deep IDE support.
- **Windsurf was completely useless**, burning credits without solving real issues.
- Opinion piece updates:
  - **CAG (Code-Augmented Generation), RAG (Retrieval-Augmented Generation), and Fine-Tuning** → Explored how AI coding assistants rely on these techniques, but each has limitations:
    - **Fine-tuning locks knowledge into a model**, making it outdated when code changes.
    - **RAG dynamically retrieves relevant code**, but retrieval accuracy and context limits create issues.
    - **CAG injects real-time code snippets**, but effectiveness depends on proper indexing and high-quality retrieval.
  - **Impact on AI-generated software** → AI coding tools risk becoming self-referential, reinforcing bad practices from previous AI-generated code.
  - **Long-term sustainability** → Hybrid models combining **fine-tuning for stable patterns, RAG for adaptability, and CAG for real-time context** may be the best solution.

### Day 19: February 19, 2025

Spent 10+ hours trying to fix the Go backend, but it was a frustrating loop of errors, misconfigurations, and unexpected issues.

**Issues Faced:**

- API endpoints were misaligned with frontend specs.
- `word_groups.json` was not loading properly.
- The database was not resetting correctly, causing duplicate/missing data.
- Groups were not being linked correctly to words.
- Pagination was broken, doubling the total word count.
- Study activities were inconsistent, and some APIs didn't return expected data.
- Error handling was unreliable across endpoints.

I first **converted the provided Go-Gin backend specs to Python-Flask**, adapting everything for **Korean language learning**. I didn't build directly from Go-Gin because I **don't know Go at all**, but I do know Python—even though I've never worked with Flask before. I figured **debugging Python errors** would be easier than dealing with **Go from scratch**, and it worked. By **breaking down the issues step by step**, I was able to fully implement the backend in **Flask before rebuilding it in Go-Gin**. In hindsight, trying to build from the **original Go-Gin specs** would have been a nightmare. By breaking it down into a structured approach, **Cursor AI was able to guide the entire process effectively**, even though I had no prior Go experience.

The setup took forever. Fixing database migrations, dependencies, and Go's quirks (CGO, SQLite, GCC, environment paths) was exhausting. The biggest challenge was getting **make, GCC, and Go to work in the same environment**, but after multiple failed setups across **Windows, WSL, and MSYS2**, I finally got everything running. Once the backend was fully implemented, **testing became another battle**. The test cases were failing because of **duplicate data inserts and pagination mismatches**, which meant rewriting how test databases were structured. After several debugging rounds, all the tests finally passed, confirming that **the Go-Gin backend is fully functional**.

**Attempts to Fix:**

- Tried multiple prompts to get AI assistance, but fixes kept breaking other parts.
- Verified JSON file loading and checked mappings.
- Investigated test failures but couldn't fully resolve database contamination.
- Considered a full rebuild instead of debugging endlessly.

**Outcome:**

💀 Got nowhere. The codebase is too messy—decided to create a new branch and start fresh rather than continue patching. Tomorrow, I'll focus on rebuilding the backend properly from the frontend + backend specs instead of fixing bad code.

**Lessons Learned:**

I've noticed that AI coding assistants often take you in circles—they apply quick fixes without fully understanding the deeper structural issues. I knew this, but I let it happen anyway, hoping for an easy path forward. Instead, I spent hours debugging patches that just introduced new problems. Sometimes, it's better to step back and rebuild from a solid foundation rather than trying to fix something that's fundamentally broken.

### Day 18: February 17, 2025

Today was a lighter day compared to yesterday's intense backend work. I finalized the **HagXwon logo**—both the **modern version and the color variations**—and I'm happy with how they turned out. I also spent time watching the backend testing video, and that's when I realized I **completely forgot to implement the dashboard.** That hit hard because I thought I was done with backend, and now I have to go back and add it.

Aside from that, I started drafting an **opinion piece on AI's Ouroboric Knowledge Loop** looking at how AI models are feeding off their own outputs and what that means for the future of knowledge generation. The piece isn't finished yet, but I spent some time researching and structuring my thoughts.

I spent most of the day trying to set up an **AI-assisted backend case study** to compare how different LLMs generate Flask API code. The goal was to structure an experiment that tracked how tools like **Copilot, Windsurf, and Cursor** handled backend tasks. But after hours of planning, I realized the setup was too complicated, and I wasn't getting the results I needed. Ultimately, I dropped the idea.

Because of this, I didn't watch any more of the backend lecture videos, and I didn't write any code today.

**Completed Work**

- **Finalized HagXwon logo** (modern + color versions).
- **Watched backend testing video** and realized I forgot the dashboard.
- **Started drafting an opinion piece** on AI's self-consuming knowledge cycle.

### Day 17: February 16, 2025

I first **converted the provided Go-Gin backend specs to Python-Flask**, adapting everything for **Korean language learning**. I didn't build directly from Go-Gin because I **don't know Go at all**, but I do know Python—even though I've never worked with Flask before. I figured **debugging Python errors** would be easier than dealing with **Go from scratch**, and it worked. By **breaking down the issues step by step**, I was able to fully implement the backend in **Flask before rebuilding it in Go-Gin**. In hindsight, trying to build from the **original Go-Gin specs** would have been a nightmare. By breaking it down into a structured approach, **Cursor AI was able to guide the entire process effectively**, even though I had no prior Go experience.

Today was about **finalizing my backend understanding and preparing for implementation.** I wanted to start coding, but I needed to make sure I wasn't going in blind.

The setup took forever. Fixing database migrations, dependencies, and Go's quirks (CGO, SQLite, GCC, environment paths) was exhausting. The biggest challenge was getting **make, GCC, and Go to work in the same environment**, but after multiple failed setups across **Windows, WSL, and MSYS2**, I finally got everything running. Once the backend was fully implemented, **testing became another battle**. The test cases were failing because of **duplicate data inserts and pagination mismatches**, which meant rewriting how test databases were structured. After several debugging rounds, all the tests finally passed, confirming that **the Go-Gin backend is fully functional**.

**Completed Work**

- **Converted AZW3 vocabulary book to JSON.**
- **Converted Go-Gin backend specs to Python-Flask (Korean).**
- **Fully implemented Flask before rebuilding in Go-Gin.**
- **Fixed CGO, SQLite, GCC, and Make integration issues.**
- **Successfully ran database migrations.**
- **Debugged and passed all backend tests.**

At this point, **both the Flask and Go-Gin backends are fully implemented and tested**. Next, I need to decide between **frontend integration or OPEA**.

## Week 1

### Day 16: February 14, 2025

I spent most of the day trying to set up an **AI-assisted backend case study** to compare how different LLMs generate Flask API code. The goal was to structure an experiment that tracked how tools like **Copilot, Windsurf, and Cursor** handled backend tasks. But after hours of planning, I realized the setup was too complicated, and I wasn't getting the results I needed. Ultimately, I dropped the idea.

Because of this, I didn't watch any more of the backend lecture videos, and I didn't write any code today.

**Completed Work**

At some point, I got sidetracked again when I found a **DRM restriction** on my Korean vocabulary book, which was frustrating because **it's literally just a list of words, and I couldn't even extract it properly.** This led me to look into **converting AZW3 files to TXT or JSON**, which ended up being way more annoying than expected. I tried multiple extraction methods, but nothing worked perfectly. Ultimately I was only able to copy over 200 words as the publisher has added copy restrictions on the book as well. I looked at other sources such as Anki and Quizlet and may end up using those instead.

Aside from that, I also thought more about my Level 5 project idea. The more I consider it, the more I realize I want **a visual-first language learning tool**, where flashcards use **images and videos instead of English translations**. I haven't locked this in yet, but it's definitely something I want to revisit once I finish the backend work.

- **Planned an AI-assisted backend coding case study** (but scrapped it).
- **Reviewed different prompting strategies for AI coding tools.**

### Day 15: February 13, 2025

Today was about **finalizing my backend understanding and preparing for implementation.** I wanted to start coding, but I needed to make sure I wasn't going in blind.

I started by **double-checking the missing API endpoints** that need to be implemented. There was some confusion about whether the homework was fully defined, so I spent time confirming that **the official documentation was incomplete** and that the real requirements were scattered across the livestreams and community discussions.

Once I had clarity, I realized that I still needed a proper **plan for execution**. I reviewed the backend structure again—specifically **how Flask Blueprints handle routing**—and went over **how to connect the frontend to the backend** using API calls.

At some point, I got sidetracked again when I found a **DRM restriction** on my Korean vocabulary book, which was frustrating because **it's literally just a list of words, and I couldn't even extract it properly.** This led me to look into **converting AZW3 files to TXT or JSON**, which ended up being way more annoying than expected. I tried multiple extraction methods, but nothing worked perfectly. Ultimately I was only able to copy over 200 words as the publisher has added copy restrictions on the book as well. I looked at other sources such as Anki and Quizlet and may end up using those instead.

Aside from that, I also thought more about my Level 5 project idea. The more I consider it, the more I realize I want **a visual-first language learning tool**, where flashcards use **images and videos instead of English translations**. I haven't locked this in yet, but it's definitely something I want to revisit once I finish the backend work.

By the end of the day, I had a clearer **execution plan for finishing the backend**, and I know exactly what I need to do next.

**Completed Work**

- **Confirmed the actual API requirements** (tech specs vs. livestream corrections).
- **Reviewed Flask Blueprints again** to make sure I understand how routing works.
- **Figured out how the frontend will connect to the backend** (API calls, CORS setup).
- **Tried to extract my Korean vocab book** but hit DRM restrictions.
- **Revisited my Level 5 idea**—thinking about flashcards with AI-generated videos.

### Day 14: February 12, 2025

I spent the entire day on backend work, research, and trying to make sense of everything. I started with the official lecture videos(6+ hrs), trying to wrap my head around the project requirements, Flask, SQLite, and how everything connects. At some point, I realized that there was no way I could do Level 5. I don't know enough about frontend, backend, or anything full-stack. Even getting Level 1 done would be a huge achievement at this point.

Then I started thinking about Copilot and Cursor, since that is the entire project, and I realised that these tools offer drop down selections for different LLMs. That led me down a rabbit hole: which model is actually capable of coding, and in which languages does it return good quality code? I needed to know. So I ended up getting a bit sidetracked and wrote a nine-page research paper breaking it all down. I believed that this exploration would allow me to shoot for level 5 and grant the highest chance of success.

After that, I tried to get back to the backend videos, but I was still confused. I took the backend and frontend specs and turned them into diagrams, hoping that seeing everything visually would help. It did, but not completely. I still felt lost. Then I started breaking down the codebase, going file by file, and finally understood that the backend is using Flask Blueprints. That's why there were no `@app.route()` functions in `app.py`, and why I was feeling lost.

I still have ~5 hours of lecture videos left, but I think I've cleared my head around the backend enough to start implementation tomorrow. I also know I'm done for the day because I'm getting snappy at my favorite AI assistant.

**Completed Work**

- Watched over six hours of backend lecture videos, covering Flask, SQLite, and API structures.
- Realized that Level 5 is completely out of reach for me, and Level 1 is the real goal.
- Wrote and published a nine-page research paper on LLM coding performance and model-language pairs.
- Created multiple diagrams to visualize the backend structure and API interactions.
- Broke down the codebase and figured out that the backend uses Flask Blueprints, finally making sense of how everything is structured.

### Day 12 & 13: February 10-11, 2025

I pulled an all-nighter and have been working for over 10 hours straight because I was falling behind in the bootcamp. I'm exhausted. Submitting the Sentence Constructor project made me realize something critical—I've spent too much time on theory and note-taking and not enough on practical application. While I'm proud of my GenAI notes and thrilled to have learned TOGAF, I should have focused on getting the practical work done first, submitted it, and then refined the theory later. Moving forward, my plan is to prioritize completing the minimum requirements first, then improve upon them instead of getting lost in details upfront.

**Completed Work:**

- Finalized and submitted the Sentence Constructor Project, completing the README, technical uncertainties, refined prompt results, and full documentation.
- Tested and iterated prompts across multiple AI models, improving structured hinting, guided learning, and response enforcement.
- Identified key takeaways from testing: AI models have a two-attempt threshold, need predefined learning paths, and require progressive difficulty scaling to avoid large jumps in complexity.
- Completed the Technical Uncertainties document, summarizing challenges with AI-powered assistants, prompt portability, and integration into standalone systems.
- Created and refined the main project README, consolidating findings from baseline testing, refined prompt testing, and prompt engineering strategies.
- Cleaned up the repository structure, ensuring logical organization of prompts, results, and documentation.
- Submitted the bootcamp project form, finalizing hypotheses, technical exploration, and outcomes.

**Big Takeaway:**
I should have completed the practical requirements first and then refined the theory at my own pace. For the next week, my priority is execution—getting things done first and improving later. No more getting stuck in details. Time to adapt and move forward.

## Week 0

### Day 11: February 9, 2025

- **Finalized and committed the main repository README**, ensuring structured documentation across all projects.
- **Created the "Project Requirements" document** to define technical constraints, architectural goals, and implementation considerations.
- **Refined TOGAF compliance tracking and AI mapping**, ensuring enterprise architecture principles are integrated into the GenAI project.
- **Developed conceptual and high-level system diagrams** using **Mermaid and eraser.io**, aligning with TOGAF's ADM framework.
- **Structured and cleaned up business case and business proposal** for the AI-powered hagwon learning platform.
- **Started working on "Sentence Constructor" project**, focusing on **NLP-based AI guidance** for structured language learning.
- **Reviewed technical uncertainty and constraints for AI-powered assistants**, identifying key risks and prompting strategies.
- **Prepared for upcoming logical and physical architecture diagrams**, ensuring alignment with bootcamp submission deadlines.

### Day 10: February 8, 2025

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

### Day 9: February 7, 2025

- Completed **TOGAF Module 3 Notes**, covering **Governance, Risk, and Techniques**.
- Refined understanding of **architecture compliance, risk management, and TOGAF techniques**.
- Attempted to create a **TOGAF Mindmap**, but found it too time-consuming and abandoned the idea.
- Went through the **ML Mini-Series by Rola Dali\*\***, an instructor for the bootcamp. Created two sets of notes:
  - **Introduction to GenAI** notes, summarizing fundamental concepts.
  - **Architecting GenAI** notes, covering structured frameworks for designing AI-driven systems.
- Continued studying **Mid-Level and Low-Level System Design**, but found it **very confusing**.
- Tried different resources and explanations but still struggling to understand **LLD application and diagramming**.

### Day 8: February 5, 2025

- Completed **TOGAF Module 2 Notes**, breaking down **ADM phases** with **BIG Questions & Themes** for better clarity.
- Ensured structured understanding with a **WHO → WHAT → WHY → HOW → WHEN → NOW** approach.
- Improved readability and flow by refining transitions between phases.
- Watched refresher videos on **High-Level Design (HLD)** and **Low-Level Design (LLD)** for System Design.
- Worked on the **High-Level Architecture** as guided in the bootcamp tutorial.
- Struggled with **Mid-Level & Low-Level Design**, currently researching best practices and structured learning resources.
- Updated the **main README** to reflect **Korean Hagwon** instead of Japanese.

### Day 7: February 4, 2025

- Spent significant time researching **TOGAF** to gain a clearer understanding of enterprise architecture.
- Attempted to read the **official TOGAF documentation**, but found it dense and difficult to navigate.
- Engaged with **enterprise architecture professionals** on Discord and Reddit to seek advice on learning strategies.
- Based on recommendations, enrolled in a **Coursera TOGAF course** (free audit option).
- Completed **Module 1** of the course and took detailed notes in **Markdown format**.

### Day 6: February 3, 2025

- Developed a detailed **business scenario** for the HagXwon AI-powered language learning platform.
- Scoped out key **functional and business requirements**, ensuring alignment with real-world hagwon industry needs.
- Researched **TOGAF and enterprise architecture** principles to understand structured methodologies for large-scale AI implementation.
- Developed a **general understanding of TOGAF ADM framework** and how it applies to AI-powered education platforms.

## Pre Bootcamp prep

### Day 5: February 1, 2025

- Expanded **BERT and fine-tuning** topics, covering **BERT, SBERT, and LoRA/RLHF techniques**.
- Completed **Data and Machine Learning** notes, refining **ML pipelines, knowledge mining, and evaluation metrics**.
- Finished **Prompt Engineering**, adding a **structured strategy table** and workflow for optimizing LLM outputs.
- Fixed **Mermaid diagrams** to improve clarity and horizontal readability.
- Prepared for next topics: **LLM Development Tools and Model Deployment Strategies**.

### Day 4: January 31, 2025

- Completed structured notes on **transformers, tokenization, and embeddings**, solidifying LLM fundamentals.
- Created **Mermaid flowcharts** to visualize key NLP processes and architecture.
- Refined **Week 00 README**, improving organization and linking correct note files.
- Debugged **math rendering issues**, ensuring proper display of formulas.
- Next focus: **BERT and fine-tuning techniques**.

### Day 3: January 30, 2025

- Completed detailed notes on **AI vs. Generative AI**, focusing on key differences, use cases, and impact.
- Wrote structured documentation on **Large Language Models (LLMs)**, covering foundational models, embeddings, transformers, and real-world applications.
- Refined **repo structure** to ensure clarity and scalability for upcoming weeks.
- Fixed **Mermaid diagrams and math rendering issues**, ensuring all visuals are properly formatted.
- Preparing for the next topic: **Tokenization & NLP fundamentals** in GenAI.

### Day 2: January 28, 2025

- Worked through **GenAI Essentials**, covering **AI vs. GenAI**, **LLMs**, and **transformers**.
- Structured my **Week 00 folder**, adding separate **note files** for key topics.
- Created a **README for Week 00** summarizing key topics and indexing notes.
- Ensured **repo structure is scalable** for future weeks of the bootcamp.

### Day 1: January 27, 2025

- Explored the **bootcamp structure, expectations, and requirements**.
- Set up the **GitHub repository** and planned the **organization of notes and projects**.
- Reviewed **GenAI Essentials course structure** and noted key topics to cover.
- Started with **AI, ML, DL fundamentals**, understanding the relationship between traditional and generative AI.
