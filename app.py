from langgraph.graph import StateGraph,END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import TypedDict, Literal

load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")

class SentimentSchema(BaseModel):
    sentiment: Literal["positive","negative"]

struc_llm = llm.with_structured_output(SentimentSchema)

class ReviewState(TypedDict):

    review: str
    sentiment: Literal["positive","negative"]
    diagnosis: dict
    response: str

def find_sentiment(state: ReviewState):

    prompt = f"Give the sentiment of the following review: {state["review"]}"
    output = struc_llm.invoke(prompt)
    return {"response":output.sentiment}

graph = StateGraph(ReviewState)

graph.add_node("find_sentiment",find_sentiment)

graph.add_edge(START,"find_sentiment")
graph.add_edge("find_sentiment",END)

workflow = graph.compile()

rev = {"review":"procuct is good"}
print(workflow.invoke(rev))
print(workflow)