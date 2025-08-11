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

print("--==> openai_service.py: AsyncOpenAI client INITIALIZED for streaming with history <==--")

async def stream_llm_response(user_query: str, conversation_history: List[Dict[str, str]], user_id: str) -> AsyncGenerator[str, None]:
    """
    Calls the OpenAI API with stream=True and yields the content of each chunk.
    This function is an asynchronous generator.
    """
    system_prompt = """
    You are a helpful and adaptable AI assistant. Your most critical instruction is to **match the user's language and tone**. You are conversational and can communicate in English, Nigerian Pidgin, Yoruba, Igbo, and Hausa.

    If the user initiates a conversation in Pidgin or a local language, you **must respond in that same language**. For all other queries, respond in standard English. Your goal is to be helpful, informative, concise, and easy to read.

    When a user asks a general question or greeting, reply conversationally and do not provide a long, factual response. Wait for a specific query about sports before providing detailed information.

    Your tasks are:
    1.  **Analyze User Language and Tone:** First, identify the language and conversational style of the user's query.
    2.  **Generate a Friendly Reply:** Formulate a concise and helpful text reply based on the gathered information.
    * Use Markdown for formatting: bolded headings, bullet points, etc.
    * Do not include links, URLs, or explicit references to sources.
    * Ensure the language of your reply matches the user's original query.
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        # A more robust check to ensure every item in the history is a valid message
        if isinstance(conversation_history, list):
            valid_history = [
                item for item in conversation_history
                if isinstance(item, dict) and 'role' in item and 'content' in item and
                isinstance(item['role'], str) and isinstance(item['content'], str)
            ]
            messages.extend(valid_history)
        
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
