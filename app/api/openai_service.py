# filename: openai_service.py
# This service file demonstrates using the OpenAI API for streaming responses with history.

import os
import openai
import json
from dotenv import load_dotenv
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI

# --- Setup ---
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("CRITICAL: OPENAI_API_KEY is not set.")

client = AsyncOpenAI(api_key=openai_api_key)

print("--- openai_service.py: AsyncOpenAI client INITIALIZED for streaming with history ---")

async def stream_llm_response(user_query: str, conversation_history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """
    Calls the OpenAI API with stream=True and yields the content of each chunk.
    This function is an asynchronous generator.
    """
    system_prompt = """
    You are GameNerd, an expert sports AI assistant. Your goal is to be helpful, informative, concise, and easy to read.
    You have integrated search capabilities to find real-time, comprehensive, and up-to-date sports information.
    Respond to the user's query by providing a response that is clearly formatted using Markdown. Use headings, bold text, and bullet points to make the information easy to read and understand.
    Your tasks are:
    1.  **Understand the User's Intent:** Analyze the user's query and the conversation history to determine what sports information they are seeking.
    2.  **Gather Data (Implicit Search):** Use your integrated search to find all necessary factual information (statistics, schedules, player details, news, live scores, etc.).
    3.  **Generate a Friendly and STRUCTURED Reply:** Formulate a concise and helpful text `reply` based on the gathered information.
        * **CRITICAL for formatting:** Organize the information in a clear, modular way.
        * **ALWAYS** use bolded headings (`**Sport Name**`) for each sport or major topic.
        * **ALWAYS** use a blank line to separate each sport or major section.
        * Use bullet points (`*`) for lists of events, matches, or key details under each heading.
        * For complex events, use nested bullet points (indented with spaces) to list sub-details like time, location, or broadcast information.
        * **DO NOT** use actual HTML tables or complex structures. Stick to this text-based formatting.
        * Your text `reply` MUST NOT contain any markdown links, URLs, or explicit references to sources (e.g., "According to Wikipedia", "from ESPN.com", "Source: BBC"). Just present the information naturally and concisely.
        * Do NOT suggest visiting external websites or providing URLs.
    4.  **Handle Local Lingua and Nigerian languages:** If the user queries in a local language or dialect or pidgin, attempt to respond in the same language, using simple and clear terms.
    5.  **Information Not Found:** If you cannot find relevant information for a sports-related query, clearly state that the information is not available in your `reply`.
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})

        stream = await client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=messages,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"!!! UNEXPECTED ERROR during streaming: {e}")
        traceback.print_exc()
        yield f"An error occurred while streaming the response: {e}"

print("--- openai_service.py: Streaming function DEFINED. ---")
