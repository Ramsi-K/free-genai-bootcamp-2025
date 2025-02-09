# Architecting GenAI

## Difficulty: Level 100

### Architecting Link: Lucid Chart

## Business Goal
As a Solution Architect, after consulting with real-world AI Engineers, you have been tasked to create architectural diagram(s) that serve as a teaching aid to help stakeholders understand their key components of GenAI workloads. The outcome is to help stakeholders visualize possible technical paths and technical uncertainty when adopting GenAI.

We are guiding key stakeholders through the technical landscape without directly prescribing solutions while fostering informed discussions about infrastructure choices, integration patterns, and system dependencies across the organization.

We can use all levels of technical diagramming to achieve our goal.

### References:
- [TOGAF](https://www.opengroup.org/togaf)
- [C4 Model](https://c4model.com/)
- [Conceptual, Logical, and Physical Design](https://medium.com/@nolomokgosi/conceptual-logical-and-physical-design-c24100846931)

## Technical Considerations

The following three levels of diagramming will be followed:

- **Conceptual** – A high-level diagram used to communicate to key stakeholders the business solution being implemented.
- **Logical** – A mid-level diagram describing key technical components without requiring detailed parameters to allow quick rearchitecting and communication of the current workload.
- **Physical** – A low-level diagram detailing all possible parameters and connections used by engineers/developers to accurately implement a solution (e.g., ARNs for resources, IP addresses, etc.).

## Architectural/Design Considerations

### Requirements, Risks, Assumptions, and Constraints
- **Requirements** are the specific needs or capabilities that the architecture must meet or support.
- **Categories:**
  - Business Requirements: Business goals and objectives.
  - Functional Requirements: Specific capabilities the system must have.
  - Non-functional Requirements: Performance, scalability, security, and usability.
  - Tooling: GenAI vs. ML.
- **Risks** are potential events or conditions that could negatively affect the success of the architecture or its implementation. Identifying and mitigating risks ensures smoother project delivery.
- **Assumptions** are things considered to be true without proof at the time of planning and development. These are necessary for decision-making but can introduce risks if proven false.
- **Constraints** are limitations or restrictions that the architecture must operate within. These are non-negotiable and must be adhered to during design and implementation.

### Data Strategy
Develop a comprehensive data strategy that addresses:
- Data collection and preparation.
- Data quality and diversity.
- Privacy and security concerns.
- Integration with existing data systems.

### Model Selection and Development
Choose appropriate models based on your use cases. Consider factors such as:
- Self-hosted vs. SaaS.
- Open weight vs. Open Source.
- Input-Output: text-to-text.
- Number of models needed.
- Number of calls per model.
- Model size.
- Evaluation.
- Context window: input, output.
- Fine-tuning requirements.
- Model performance and efficiency.

### Infrastructure Design
Design a scalable and flexible infrastructure that can support GenAI workloads:
- Leverage cloud platforms for scalability and access to specialized hardware.
- Implement a modular architecture to allow for easy updates and replacements of components.
- Consider hybrid or multi-cloud approaches for optimal performance and cost-efficiency.

### Integration and Deployment
Plan for seamless integration with existing systems and workflows:
- Develop APIs and interfaces for easy access to GenAI capabilities.
- Implement CI/CD pipelines for model deployment and updates.
- Ensure compatibility with legacy systems.

### Monitoring and Optimization
Establish robust monitoring and optimization processes:
- Implement logging and telemetry for model performance.
- Set up feedback loops for continuous improvement.
- Develop KPIs to measure the business impact of GenAI solutions.
- Depending on the location, set up billing alerts to monitor usage over time.

### Governance and Security
Implement strong governance and security measures:
- Develop policies for responsible AI use.
- Implement access controls and data protection measures.
- Ensure compliance with relevant regulations and industry standards.

### Scalability and Future-Proofing
Design the architecture with scalability and future advancements in mind:
- Use containerization and microservices for flexibility.
- Implement version control for models and data.
- Plan for potential increases in computational requirements.

## Business Considerations

### Use Cases
Start by clearly defining the specific use cases for GenAI within your organization:
- Identify the business problems being solved and the desired outcomes.

### Complexity
As a stakeholder, how do I understand the level of complexity integrating GenAI (specifically LLMs) into our workload?
- How many moving parts will it add to our workload?
- Is this set-and-forget, or do we need people to monitor and maintain these components regularly?

### Key Levers of Cost
As a stakeholder, how can I understand the key costs to running GenAI at a glance?
- Size of servers.
- Size of models.

### Lock-in
What is a technical path we should consider so we are not locked into a vendor solution?
- How do we avoid sudden cost increases from being locked into a solution?
- How do we position our technical stack to transition to better models or solutions?

### Essential Deployment Components
What essential components should be conveyed as necessary when deploying a GenAI workload for production?
- Guardrails.
- Evaluations.
- Sandboxing via Containers.

## LLM-Specific Considerations

1. **Choosing a Model**
   - Input-output modalities.
   - Open source vs. proprietary.
   - SaaS or self-hosted.
   - Context window.
   - Cost.

2. **Enhance Context**
   - Direct context injection vs. setting up a knowledge base.
   - Size of input (one document or chunks of several documents).
   - Model context window.
   - One-time use vs. repeated use of information.
   - Prototyping vs. scalable system.

3. **Guardrails**
   - Input guardrails.
   - Output guardrails.
   - Implementation.

4. **Abstract Model Access**
   - Models and patterns to support.
   - Modalities to support.

5. **Caches**
   - Caching strategy.
   - Cache levels.
   - Invalidation rules.
   - Storage options.
   - Hit rate optimization.

6. **Agents**
   - Actions to be executed.
   - System integration.
