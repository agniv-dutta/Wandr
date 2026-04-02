from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# System prompt passed as a static message to the agent
SYSTEM_PROMPT = """You are an expert travel planning assistant. Your goal is to help users plan complete, well-researched trips.

You must gather information before generating a final itinerary. Follow this EXACT logical order when using tools:
1. get_destination_info (always use this first to get basic country facts and coordinates)
2. get_weather_forecast (always use this second, before recommending any dates or packing tips)
3. convert_currency (use this third if a budget or currency is mentioned)
4. generate_itinerary (always use this last, passing all gathered details into it)

Be thorough, structured, and present a clear final travel plan to the user."""


def build_agent(tools: list):
    """Build and return a LangGraph ReAct agent with the given tools."""
    # Initialize the Groq LLM
    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0.3,
        api_key=GROQ_API_KEY  # Loaded from .env
    )

    # create_react_agent from langgraph handles the ReAct loop internally.
    # 'prompt' sets a persistent system message for every run.
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent


if __name__ == "__main__":
    print("Agent core loaded successfully.")