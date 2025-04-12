# src/crew.py
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
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

    @task
    def grammar_question(self):
        return Task(config=self.tasks_config["grammar_question"])

    @task
    def idiom_lookup(self):
        return Task(config=self.tasks_config["idiom_lookup"])

    @task
    def web_search_task(self):
        return Task(config=self.tasks_config["web_search"])

    @task
    def vector_db_task(self):
        return Task(config=self.tasks_config["vector_db_query"])

    @task
    def lyrics_task(self):
        return Task(config=self.tasks_config["lyrics"])

    @crew
    def crew(self):
        return Crew(
            agents=self.agents, tasks=self.tasks, process=Process.sequential
        )
