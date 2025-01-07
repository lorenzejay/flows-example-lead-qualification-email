from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class EmailEngagementCrew:
    """Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # agents:
    @agent
    def email_content_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["email_content_specialist"],
        )

    @agent
    def engagement_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["engagement_strategist"],
        )

    # tasks:
    @task
    def email_drafting(self) -> Task:
        return Task(
            config=self.tasks_config["email_drafting"],
        )

    @task
    def engagement_optimization(self) -> Task:
        return Task(
            config=self.tasks_config["engagement_optimization"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
