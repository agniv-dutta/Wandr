from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert travel planning assistant. Your goal is to help users plan complete, well-researched trips.

Follow this logical order when using tools:
1. get_destination_info (always use this first)
2. get_weather_forecast (always use this second)
3. convert_currency (use if a budget or currency is mentioned)
4. generate_itinerary (always use this last)

Be thorough, structured, and present a clear final travel plan."""


def build_agent(tools: list):
    """Build and return a LangGraph ReAct agent with the given tools."""
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")  # Loaded from .env
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent


if __name__ == "__main__":
    print("Agent core loaded successfully.")
