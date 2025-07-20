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
struc_llm.invoke("product is very good")