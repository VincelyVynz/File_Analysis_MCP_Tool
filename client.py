import os, asyncio, json
from dotenv import load_dotenv
from groq import Groq
from fastmcp import Client

load_dotenv()

LLM_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
MAX_MEMORY = 10
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


messages = [
    {
        "role": "system",
        "content": (
            """
            You are a file analysis assistant.
            
            CRITICAL TOOL USAGE RULES:
            - Only call a tool when the user gives a clear, specific, and explicit instruction to perform an operation.
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
    },
    {
        "type": "function",
        "function": {
            "name" : "read_excel",
            "description": "Read contents of an Excel file and return a pandas dictionary",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "filepath" : {"type" : "string"},
                },
                "required" : ["filepath"]
            }
        }
    }
]

# Call LLM

async def handle_turn(user_input, mcp_client):
    messages.append({
        "role": "user",
        "content": user_input
    })

    response = groq_client.chat.completions.create(
        model = LLM_MODEL,
        messages = messages,
        tools = tools,
        tool_choice = "auto"
    )

    # Extract text reply from LLM response
    msg = response.choices[0].message

    # Adding to message history
    messages.append(msg)

    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            raw_args = json.loads(tool_call.function.arguments)

            try:
                call_result = await mcp_client.call_tool(tool_name, raw_args)

                if call_result.is_error:
                    result_text = f"Error: {call_result.content}"
                else:
                    result_text = ""
                    if hasattr(call_result, 'content') and isinstance(call_result.content, list):
                        for content in call_result.content:
                            if hasattr(content, 'text'):
                                result_text += content.text
                            else:
                                result_text += str(content)
                    else:
                        result_text = str(call_result)

            except Exception as e:
                result_text = f"Error: {str(e)}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text
            })

        final_response = groq_client.chat.completions.create(
            model = LLM_MODEL,
            messages = messages,
        )

        final_msg = final_response.choices[0].message
        print(final_msg.content)
        messages.append(final_msg)

    else:
        print(msg.content)

    if len(messages) > MAX_MEMORY:
        messages[:] = [messages[0]] + messages[-MAX_MEMORY:]


async def main():
    print("FastMCP File Analysis Bot")
    print("Type 'exit' or 'quit' to quit\n\n")

    async with Client(MCP_SERVER_URL) as mcp_client:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            await handle_turn(user_input, mcp_client)

if __name__ == "__main__":
    asyncio.run(main())