# AI Tool-Calling Assistant

A local AI assistant built with Python, LangChain, LangGraph, and Ollama.

The assistant uses an LLM-powered agent to interpret natural-language requests and select the appropriate tool to complete the task.

## Features

- Calculator and numerical calculations
- Unit and numerical conversions
- Current date and time
- Current weather information
- Wikipedia information retrieval
- General conversation
- Error handling for failed tool requests
- Local LLM inference using Ollama

## Technologies Utilized
- Python
- LangChain
- LangGraph
- Ollama
- Requests
- uv

## How It Works

The user sends a request to the AI agent.

The agent determines whether a tool is needed, selects the appropriate tool, receives the result, and generates a natural-language response.

User Text
  ↓
AI Agent
  ↓
Tool Selection (Calculator, Date/Time, Weather, or the Wikipedia Tool)
  ↓
Tool Result
  ↓
AI Response

## Example Queries
What is 928 × 47?

What time is it in Tokyo?

What's the weather in Toronto?

Who was Albert Einstein?

(The agent determines which tool is most appropriate for each request)

## Setup
1. Install Dependencies - uv sync
2. Install Ollama and make sure it is running.
3. Download the Model - ollama run gpt-oss:20b
4. Run the Assistant - uv run main.py

## What I Learned
This project helped me understand how LLM-powered agents interact with external tools. I learned how to create custom Python tools, connect a local language model to LangChain, build an agent workflow with LangGraph, integrate external APIs, and handle tool failures.

## Future Improvements
- Conversation memory
- Additional tools
- Automated tests
- Graphical user interface
Additional tools
Automated tests
Graphical user interface
