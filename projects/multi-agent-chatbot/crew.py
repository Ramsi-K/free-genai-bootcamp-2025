from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class KoreanTutoringCrew():
    @agent
    def ahjumma_gpt(self): ...
    
    @agent
    def ahjussi_gpt(self): ...

    @task
    def grammar_question(self): ...

    @task
    def idiom_lookup(self): ...

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential
        )
