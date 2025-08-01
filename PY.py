# filename: assistant_web_search.py

import os
import time
import openai
from dotenv import load_dotenv

# --- Setup ---
# Load environment variables from a .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
# IMPORTANT: Never hardcode your API key directly in your code.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)

print("OpenAI client initialized.")

def create_assistant_for_web_search():
    """
    Creates or retrieves an Assistant configured for web searching.
    We'll create a new one each time for simplicity in this example.
    """
    print("Creating a new Assistant with web_search tool enabled...")
    try:
        assistant = client.beta.assistants.create(
            name="Real-time Web Search Assistant",
            instructions="You are a helpful assistant that can search the web for real-time information.",
            model="gpt-4o",
            tools=[{"type": "web_search"}] # This is the key tool for real-time data
        )
        print(f"Assistant created with ID: {assistant.id}")
        return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

def main():
    """
    Main function to orchestrate the Assistant API workflow.
    """
    assistant = create_assistant_for_web_search()
    if not assistant:
        print("Failed to create assistant. Exiting.")
        return

    # --- Step 2: Create a Thread ---
    # A thread represents a conversation session.
    print("\nCreating a new Thread...")
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    user_query = "What is the latest news on the recent space mission launch?"

    # --- Step 3: Add a Message to the Thread ---
    # We add the user's query as the first message.
    print(f"\nAdding user message to the Thread: '{user_query}'")
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_query
    )

    # --- Step 4: Create and Run the Assistant ---
    # This triggers the assistant to process the messages in the thread.
    print("\nCreating a Run to execute the Assistant...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # --- Step 5: Poll the Run Status until it's completed ---
    # The API is asynchronous, so we need to wait for the run to finish.
    print(f"Run started with ID: {run.id}. Waiting for it to complete...")
    
    while run.status != "completed":
        # Retrieve the run's current status
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {run.status}")
        time.sleep(2) # Wait for a couple of seconds before polling again

    print("\nRun completed successfully!")

    # --- Step 6: Retrieve and Print the Messages ---
    # Get all messages from the thread to see the assistant's response.
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Print the assistant's response
    print("\n--- Assistant's Response ---")
    # Messages are in reverse chronological order, so we reverse the list.
    for message in reversed(messages.data):
        if message.role == "assistant":
            # The response content is often in a list of content objects
            for content in message.content:
                if content.type == "text":
                    print(content.text.value)

    # --- Clean up: Optional ---
    # Deleting the assistant is a good practice to avoid clutter.
    # Note: Threads can be deleted separately if you wish.
    print("\nCleaning up by deleting the assistant...")
    # This is currently not supported in the latest API versions but good to keep in mind.
    # In a real-world app, you might reuse an assistant instead of deleting it.
    # client.beta.assistants.delete(assistant.id)
    # print(f"Assistant with ID {assistant.id} deleted.")

if __name__ == "__main__":
    main()
