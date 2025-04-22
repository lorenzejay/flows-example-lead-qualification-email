#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start

from .crews.lead_qualification_crew.lead_qualification_crew import (
    LeadQualificationCrew,
    LeadPersonalInfo,
    CompanyInfo,
    LeadScore,
)
from .crews.email_engagement_crew.email_engagement_crew import EmailEngagementCrew


class LeadQualificationState(BaseModel):
    lead_score: LeadScore = LeadScore(score=0, scoring_criteria=[], validation_notes="")
    personal_info: LeadPersonalInfo = LeadPersonalInfo(
        name="",
        job_title="",
        role_relevance=0,
        professional_background="",
    )
    company_info: CompanyInfo = CompanyInfo(
        company_name="",
        industry="",
        company_size=0,
        revenue=0,
        market_presence=0,
    )


class LeadQualificationFlow(Flow[LeadQualificationState]):
    @start()
    def generate_lead_score(self):
        result = (
            LeadQualificationCrew()
            .crew()
            .kickoff(
                {
                    "lead_data": """
                {
                    Name: João Moura
                    Job Title: Director of Engineering
                    Company: Clearbit
                    Email: joao@clearbit.com
                    Use case: Using AI Agent to do better data enrichment.
                }
                                                """
                }
            )
        )
        print("Lead score generated", result)
        self.state.lead_score = result.pydantic.lead_score
        self.state.personal_info = result.pydantic.personal_info
        self.state.company_info = result.pydantic.company_info

    @listen(generate_lead_score)
    def generate_lead_email(self):
        if self.state.lead_score.score > 70:
            print("state", self.state)
            result = (
                EmailEngagementCrew()
                .crew()
                .kickoff(
                    inputs={
                        "personal_info": str(self.state.personal_info),
                        "company_info": str(self.state.company_info),
                        "lead_score": str(self.state.lead_score.score),
                    }
                )
            )

        print("Email generated", result.raw)
        self.state.lead_score = result.raw
        self.state.personal_info = result.raw


def kickoff():
    lead_qualification_flow = LeadQualificationFlow()
    lead_qualification_flow.kickoff()


def plot():
    lead_qualification_flow = LeadQualificationFlow()
    lead_qualification_flow.plot()


if __name__ == "__main__":
    kickoff()
