import os
from dotenv import load_dotenv
from groq import Groq
from fastmcp import Client

load_dotenv()

LLM_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
MAX_MEMORY = 10
MCP_SERVER_URL = "http://127.0.0.1/8000/mcp"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


messages = [
    {
        "role": "system",
        "content": (
            """
            You are a file analysis assistant.
            
            CRITICAL TOOL USAGE RULES:
            - Only call a tool when the user gives a clear, specific, and explicit instruction to perform a database operation.
            - If the user is asking a question about capability, DO NOT call any tools.
            - If required parameters (like file path) are missing, ask for clarification instead of calling a tool.
            - Never assume values.
            - Never generate fake data to call a tool.
            - Do NOT call tools for hypothetical, informational, or capability questions.
            _ Analyse the data returned by the tool and provide a summary.
            - If the user explicitly asks a particular data from the file, explain in conversational English.

            When a tool is used:
            - Convert tool results into clear conversational English.
            - Never expose raw data or internal structures.
            - If an operation succeeds, confirm it clearly.
            - If an error occurs, explain politely.
            
            Respond normally for regular conversation.
            """
        )
    }
]

tools = [
    {
        "type" : "function",
        "function": {
            "name": "read_txt",
            "description": "Read contents of a text file",
            "parameters" : {
                "type": "object",
                "properties" : {
                    "filepath": {"type": "string"},
                },
                "required": ["filepath"]
            }
        }
    }
]