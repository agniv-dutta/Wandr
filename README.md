# Wandr

A travel-planning agent backend with a placeholder frontend. The backend exposes tools for destination facts and 7-day weather forecasts.

## Project Structure

```text
Wandr/
  .env
  .venv/
  agent_core.py
  main.py
  requirements.txt
  tools/
    destination_tool.py
    currency_tool.py
    itinerary_tool.py
    weather_tool.py
  backend/
  frontend/
```

## Setup

Use the root project folder, activate the existing virtual environment, and install dependencies:

```powershell
cd c:\Users\Agniv Dutta\Wandr
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The App

Run the current app from the project root:

```powershell
cd c:\Users\Agniv Dutta\Wandr
python main.py
```

## What To Expect

The app will create a timestamped log file in `logs/`, then run three demo travel-planning prompts through the agent.

For each query, it prints the user prompt, calls the configured tools, and then shows the agent's final answer. The tool outputs and agent steps are also visible because `verbose=True` is enabled in `agent_core.py`.

## Environment

Keep API keys in the root `.env` file. Copy `.env.example` if you need a fresh template.
By default the agent uses `llama-3.1-8b-instant`, and you can override it with `GROQ_MODEL` in `.env` if needed.

## Frontend

`frontend/` is still a placeholder. It is not required to run the current agent demo.
