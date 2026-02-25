import os
import sys
from datetime import datetime
from typing import Optional
from langgraph.types import Send

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import get_buffer_string
from langchain_community.tools.tavily_search import TavilySearchResults

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.backend_server.model import (
    Analyst,
    Perspectives,
    GenerateAnalystsState,
    InterviewState,
    ResearchGraphState,
    
)

from src.utils.model_loader import ModelLoader

from src.utils.model_loader import ModelLoader
from src.prompt_lib.prompts import *

def build_interview_graph(llm,tavily_search=None):

    memory = MemorySaver()

    def generation_question(state:InterviewState):
        """_summary_

        Args:
            state (InterviewState): _description_
        """
        pass

    def search_web(state: InterviewState):
        """_summary_

        Args:
            state (InterviewState): _description_
        """
        pass

    def generate_answer(state: InterviewState):
        """_summary_

        Args:
            state (InterviewState): _description_
        """
        pass

    def save_interview(state: InterviewState):
        """_summary_

        Args:
            state (InterviewState): _description_
        """
        pass

    def write_section(state: InterviewState):
        """_summary_

        Args:
            state (InterviewState): _description_
        """
        pass

    builder = StateGraph(InterviewState)


class AutonomousReportGenerator:
    def __init__(self, llm):
        """_summary_
        """
        self.llm = llm
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults()
    
    def create_analyst(self,state:GenerateAnalystsState):
        """_summary_
        """
        structured_llm = self.llm.with_structured_output(Perspectives)
        
        analysts = structured_llm.invoke([
            SystemMessage(content=CREATE_ANALYSTS_PROMPT),
            HumanMessage(content="Generate the set of analysts.")
        ])
        return {"analysts": analysts.analysts}
    
    def human_feedback(self):
        """_summary_
        """
        pass
    
    def write_report(self, state: ResearchGraphState):
        """_summary_
        """
        sections = state.get("sections", [])
        topic = state.get("topic", "")
        system_message = f"You are compiling a unified research report on: {topic}."
        if not sections:
            sections = ["No sections generated — please verify interview stage."]
    
        report = self.llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content="\n\n".join(sections))
        ])
        return {"content": report.content}
            
    def write_introduction(self,state:ResearchGraphState):
        topic = state["topic"]
        intro = self.llm.invoke([
            SystemMessage(content=f"Write a 100-word markdown introduction for {topic}.")
        ])
        return {"introduction": intro.content}
    
    def write_conclusion(self, state:ResearchGraphState):
        """_summary_
        """
        pass
    
    def finalize_report(self, state:ResearchGraphState):
        """_summary_
        """
        pass
    
    def save_report(self, final_report: str, topic: str, format: str = "docx", save_dir: str = None):
        """_summary_
        """
        pass
    
    def _save_as_docx(self, text:str,file_path:str):
        """'_summary_'
        """
        pass
    
    def _save_as_pdf(self, text:str,file_path:str):
        """_summary_
        """
        pass
    
    def build_graph(self):
        """_summary_
        """
        builder = StateGraph(ResearchGraphState)
        
        interview_graph = build_interview_graph(self.llm, self.tavily_search)
        
        def initiate_all_interviews(state: ResearchGraphState):
            topic = state["topic"]
            analysts = state.get("analysts", [])
            if not analysts:
                print("No analysts found — skipping interviews.")
                return END
            # Create one Send() event per analyst
            return [
                Send(
                    "conduct_interview",
                    {
                        "analyst": analyst,
                        "messages": [HumanMessage(content=f"So, let's discuss about {topic}.")],
                        "max_num_turns": 2,
                        "context": [],
                        "interview": "",
                        "sections": [],
                    },
                )
                for analyst in analysts
            ]


        builder.add_node("create_analyst", self.create_analyst)
        builder.add_node("human_feedback", self.human_feedback)
    
if __name__ == "__main__":
        """_summary_
        """
        llm = ModelLoader().load_llm()
        # print(llm.invoke("hii").content)
        
        reporter = AutonomousReportGenerator()
        reporter.build_graph()
        graph = reporter.build_graph()
        
        topic = ""
        
        thread = {"configurable": {"thread_id": "1"}}
        
        for _ in graph.stream({"topic": topic, "max_analysts": 3}, thread, stream_mode="values"):
            """_summary_
            """
            pass

        state = graph.get_state(thread)
        
        feedback = input("\n Enter your feedback or press Enter to continue as is: ").strip()

        graph.update_state(thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
        
        for _ in graph.stream(None, thread, stream_mode="values"):pass

        final_state = graph.get_state(thread)
        final_report = final_state.values.get("final_report")

        if final_report:
            reporter.save_report(final_report, topic, "docx")
            reporter.save_report(final_report, topic, "pdf")
            
        else:
            print("No Report Content Generated")

            