from langgraph.graph import StateGraph,END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import TypedDict, Literal

load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")

class SentimentSchema(BaseModel):
    sentiment: Literal["positive","negative"]

class DiagnosisSchema(BaseModel):
    issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"]
    tone: Literal["angry", "frustrated", "disappointed", "calm"]
    urgency: Literal["low", "medium", "high"]


struc_llm = llm.with_structured_output(SentimentSchema)
struc_llm2 = llm.with_structured_output(DiagnosisSchema)

class ReviewState(TypedDict):

    review: str
    sentiment: Literal["positive","negative"]
    diagnosis: dict
    response: str

def find_sentiment(state: ReviewState):

    prompt = f"Give the sentiment of the following review: {state["review"]}"
    output = struc_llm.invoke(prompt).sentiment
    return {"response":output}

def cheack_point(state: ReviewState) -> Literal["positive_response","run_diagnosis"]:
    if state["sentiment"] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"
    
def positive_response(state: ReviewState):
    
    prompt = f"""Write a warm thank-you message in response to this review:
                \n\n\"{state['review']}\"\n
                Also, kindly ask the user to leave feedback on our website. Give this link for feedback"""
    output = llm.invoke(prompt).content
    return {"response":output}

def run_diagnosis(state: ReviewState):

    prompt = f"""Diagnose this negative review:\n\n{state['review']}\nReturn issue_type, tone, and urgency."""
    output = struc_llm2.invoke(prompt)
    return {"response":output.model_dump}

def negative_response(state: ReviewState):

    diagnosis = state["diagnosis"]

    prompt = f"""You are a support Assitant.
    the user had a {diagnosis["issue_type"]} issue, sounded {diagnosis["tone"]}, and marked up as {diagnosis["urgency"]}.
    Write an empathetic, helpful resolution message."""

    output = llm.invoke(prompt).content
    return {"response": output}

graph = StateGraph(ReviewState)
graph.add_node("find_sentiment",find_sentiment)
graph.add_node("positive_response",positive_response)
graph.add_node("run_diagnosis",run_diagnosis)
graph.add_node("negative_response",negative_response)

graph.add_edge(START,"find_sentiment")

graph.add_conditional_edges("find_sentiment",cheack_point)


graph.add_edge("positive_response", END)
graph.add_edge("run_diagnosis", "negative_response")
graph.add_edge("negative_response", END)

workflow = graph.compile()

rev = {"review":"procuct is good"}
print(workflow.invoke(rev))

print(workflow.get_graph().draw_ascii())