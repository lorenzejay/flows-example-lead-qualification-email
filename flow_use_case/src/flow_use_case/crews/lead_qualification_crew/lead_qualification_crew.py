from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field
from typing import List, Optional


# Create Pydantic Models for Structured Output
class LeadPersonalInfo(BaseModel):
    name: str = Field(..., description="The full name of the lead.")
    job_title: str = Field(..., description="The job title of the lead.")
    role_relevance: int = Field(
        ...,
        ge=0,
        le=10,
        description="A score representing how relevant the lead's role is to the decision-making process (0-10).",
    )
    professional_background: Optional[str] = Field(
        None, description="A brief description of the lead's professional background."
    )


class CompanyInfo(BaseModel):
    company_name: str = Field(
        ..., description="The name of the company the lead works for."
    )
    industry: str = Field(
        ..., description="The industry in which the company operates."
    )
    company_size: int = Field(
        ..., description="The size of the company in terms of employee count."
    )
    revenue: Optional[float] = Field(
        None, description="The annual revenue of the company, if available."
    )
    market_presence: int = Field(
        ...,
        ge=0,
        le=10,
        description="A score representing the company's market presence (0-10).",
    )


class LeadScore(BaseModel):
    score: int = Field(
        ..., ge=0, le=100, description="The final score assigned to the lead (0-100)."
    )
    scoring_criteria: List[str] = Field(
        ..., description="The criteria used to determine the lead's score."
    )
    validation_notes: Optional[str] = Field(
        None, description="Any notes regarding the validation of the lead score."
    )


class LeadScoringResult(BaseModel):
    personal_info: LeadPersonalInfo = Field(
        ..., description="Personal information about the lead."
    )
    company_info: CompanyInfo = Field(
        ..., description="Information about the lead's company."
    )
    lead_score: LeadScore = Field(
        ...,
        description="The final validated score for the lead, including scoring criteria and validation notes.",
    )


@CrewBase
class LeadQualificationCrew:
    """Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # agents:
    @agent
    def lead_data_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_data_agent"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @agent
    def cultural_fit_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["cultural_fit_agent"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @agent
    def scoring_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["scoring_validation_agent"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    # tasks:
    @task
    def lead_data_collection(self) -> Task:
        return Task(
            config=self.tasks_config["lead_data_collection"],
            output_pydantic=LeadPersonalInfo,
        )

    @task
    def cultural_fit_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["cultural_fit_analysis"],
            output_pydantic=CompanyInfo,
        )

    @task
    def lead_scoring_and_validation(self) -> Task:
        return Task(
            config=self.tasks_config["lead_scoring_and_validation"],
            output_pydantic=LeadScoringResult,
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
