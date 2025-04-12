# src/crew.py
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from src.tools.web_search import WebSearchAgent
from src.tools.vector_db_agent import VectorDBAgent
from src.tools.ollama import OllamaTool
from src.tools.lyrics_fetcher import LyricsFetcher


@CrewBase
class KoreanTutoringCrew:
    @agent
    def ahjumma_gpt(self):
        from src.agents.ahjumma_gpt import AhjummaGPT

        return AhjummaGPT()

    @agent
    def ahjussi_gpt(self):
        from src.agents.ahjussi_gpt import AhjussiGPT

        return AhjussiGPT()

    @agent
    def web_search_agent(self):
        return WebSearchAgent()

    @agent
    def vector_db_agent(self):
        return VectorDBAgent()

    @agent
    def lyrics_agent(self):
        return LyricsFetcher()

    @before_kickoff
    def process_inputs(self, inputs):
        """
        Process inputs before kickoff.
        This method is called before the crew starts.
        """
        query = inputs.get("query", "")
        task_type = inputs.get("task_type", "grammar_question")

        print(f"Processing query: '{query}' as task type: {task_type}")

        # Create the appropriate task based on task type and store it in a variable
        created_task = None

        if task_type == "grammar_question":
            created_task = self.grammar_question(input=query)
        elif task_type == "idiom_lookup":
            created_task = self.idiom_lookup(input=query)
        elif task_type == "web_search":
            created_task = self.web_search_task(input=query)
        elif task_type == "vector_db_query":
            created_task = self.vector_db_task(input=query)
        elif task_type == "lyrics":
            created_task = self.lyrics_task(input=query)
        else:
            # Default to grammar question
            created_task = self.grammar_question(input=query)

        # Only append the task if it was created successfully
        if created_task:
            self.tasks.append(created_task)
            print(f"Created task of type {task_type}")

        return inputs

    @task
    def grammar_question(self, input=None, context=None):
        task_config = self.tasks_config["grammar_question"]
        # Ensure context is a list or None
        context_list = (
            context
            if isinstance(context, list) or context is None
            else [context]
        )
        return Task(config=task_config, input=input, context=context_list)

    @task
    def idiom_lookup(self, input=None, context=None):
        task_config = self.tasks_config["idiom_lookup"]
        # Ensure context is a list or None
        context_list = (
            context
            if isinstance(context, list) or context is None
            else [context]
        )
        return Task(config=task_config, input=input, context=context_list)

    @task
    def web_search_task(self, input=None, context=None):
        task_config = self.tasks_config["web_search"]
        # Ensure context is a list or None
        context_list = (
            context
            if isinstance(context, list) or context is None
            else [context]
        )
        return Task(config=task_config, input=input, context=context_list)

    @task
    def vector_db_task(self, input=None, context=None):
        task_config = self.tasks_config["vector_db_query"]
        # Ensure context is a list or None
        context_list = (
            context
            if isinstance(context, list) or context is None
            else [context]
        )
        return Task(config=task_config, input=input, context=context_list)

    @task
    def lyrics_task(self, input=None, context=None):
        task_config = self.tasks_config["lyrics"]
        # Ensure context is a list or None
        context_list = (
            context
            if isinstance(context, list) or context is None
            else [context]
        )
        return Task(config=task_config, input=input, context=context_list)

    @crew
    def crew(self):
        return Crew(
            agents=self.agents, tasks=self.tasks, process=Process.sequential
        )
