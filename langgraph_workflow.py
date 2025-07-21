
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
    return {"sentiment":output}

def cheack_point(state: ReviewState) -> Literal["positive_response","run_diagnosis"]:
    if state["sentiment"] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"
    
def positive_response(state: ReviewState):
    prompt = f"""
    A customer left the following product review: "{state['review']}"

    Write a short, friendly 2-line thank-you message as a seller on an e-commerce site (like Amazon or Flipkart).
    Acknowledge their kind words, and politely invite them to leave detailed feedback on our website: <a href="https://www.linkedin.com/in/bantee-sharma-9a970b26b/">Click here to leave feedback</a>
    Keep the tone warm, professional, and concise.
    """
    output = llm.invoke(prompt).content
    return {"response": output}

def run_diagnosis(state: ReviewState):

    prompt = f"""Diagnose this negative review:\n\n{state['review']}\nReturn issue_type, tone, and urgency."""
    output = struc_llm2.invoke(prompt)
    return {"diagnosis":output.model_dump()}

def negative_response(state: ReviewState):
    diagnosis = state["diagnosis"]

    prompt = f"""
    A customer left a negative product review. Based on the diagnosis:
    - Issue Type: {diagnosis['issue_type']}
    - Tone: {diagnosis['tone']}
    - Urgency: {diagnosis['urgency']}

    Write a short, **2-3 line empathetic message** as a seller on Amazon/Flipkart. Apologize briefly, acknowledge the issue, and invite the customer to connect with us for resolution.

    End the message with: <a href="https://www.linkedin.com/in/bantee-sharma-9a970b26b/" target="_blank">Click here to share details</a>
    Keep it friendly, professional, and concise.
    """
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


def process_review(review: str):
    state = {"review": review}
    result = workflow.invoke(state)
    return result