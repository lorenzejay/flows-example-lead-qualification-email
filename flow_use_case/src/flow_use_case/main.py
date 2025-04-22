#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router
from crewai.llm import LLM
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

    @router(generate_lead_score)
    def check_approval(self, previous_result):
        if self.state.lead_score.score > 70:
            return "approved"
        else:
            return "rejected"

    @listen("approved")
    def generate_lead_email(self):
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

    @listen("rejected")
    def generate_rejection_email(self):
        result = LLM(model="gpt-4o-mini").call(
            messages=[
                {
                    "role": "system",
                    "content": f"""
            You are a sales agent.
            You are given a lead that was rejected.
            You need to generate a rejection email to the lead.
            The lead is:
            {self.state.personal_info}
            {self.state.company_info}
            {self.state.lead_score}
            """,
                },
                {
                    "role": "user",
                    "content": "Generate a rejection email to the lead.",
                },
            ]
        )
        print("Rejection email generated", result)


def kickoff():
    lead_qualification_flow = LeadQualificationFlow()
    lead_qualification_flow.kickoff()


def plot():
    lead_qualification_flow = LeadQualificationFlow()
    lead_qualification_flow.plot()


if __name__ == "__main__":
    kickoff()
