import logging
import os
import time
from dotenv import load_dotenv
import openai
import streamlit


load_dotenv()

client = openai.OpenAI()

model = "gpt-3.5-turbo-0125"

# Upload file to OpenAI embedddings
filepath = "./cryptocurrency.pdf"
file_object = client.files.create(file=open(filepath, "rb"),
                                  purpose="assistants")

thread_id="thread_vtLkY5t23kN5bUVHbR8jzfrc"
assis_id="asst_gGefAJSq5zRl87DRmge9BwtA"

#Step 3 Create a thread
message="What is mining?"
# thread = client.beta.threads.create()
# thread_id = thread.id
# print(thread_id)

message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message
)


#Run Assistant
run=client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assis_id,
    instructions="Please address the user as Bruce"
)

def wait_for_completion(client, thread_id, run_id, sleep_interval=5):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


wait_for_completion(client=client,
                    thread_id=thread_id,
                    run_id=run.id)
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id,run_id=run.id,)
print(f"Run Steps --> {run_steps.data[0]}")