import logging
import os
import time
from dotenv import load_dotenv
import openai
import streamlit as st


load_dotenv()

client = openai.OpenAI()

model = "gpt-3.5-turbo-0125"

thread_id="thread_vtLkY5t23kN5bUVHbR8jzfrc"
assis_id="asst_gGefAJSq5zRl87DRmge9BwtA"

#Initialzie all Session
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id=None

# Set up font End page
st.set_page_config(
    page_title="Study Buddy",
    page_icon=":books:"
)    


# Function Definition
def upload_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    
    return response.id

# Side Bar, where users can upload file

file_uploaded=st.sidebar.file_uploader(
    "Uload a file to be transformed into embeddings", key="file_upload"
)

#upload file button - save the file id
if st.sidebar.button("Upload File"):
    if file_uploaded:
        with open(f"{file_uploaded.name}","wb") as f:
            f.write(file_uploaded.getbuffer())
        another_file_id = upload_to_openai(f"{file_uploaded.name}")
        st.session_state.file_id_list.append(another_file_id)
        st.sidebar.write(f"File Id :: {another_file_id}")

# Display those file id's
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File Ids : " )
    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id)
        #Associate each file id with the current assistamt
        assistant_file=client.beta.assistants.files.create(
            assistant_id=assis_id,
            file_id=file_id
        )

#BButton to initiate the chat session
if st.sidebar.button("Start chatting..."):
    if st.session_state.file_id_list:
        st.session_state.start_chat=True

        chat_thread = client.beta.threads.create()
        st.session_state.thread_id = chat_thread.id
        st.write("Thread Id: ", chat_thread.id)
    else:
        st.sidebar.warning("No Files found.")

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = (
        message_content.annotations if hasattr(message_content, "annotations") else []
    )
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(
            annotation.text, f" [{index + 1}]"
        )

        # Gather citations based on annotation attributes
        if file_citation := getattr(annotation, "file_citation", None):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {
                "filename": "cryptocurrency.pdf"
            }  # This should be replaced with actual file retrieval
            citations.append(
                f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}'
            )
        elif file_path := getattr(annotation, "file_path", None):
            # Placeholder for file download citation
            cited_file = {
                "filename": "cryptocurrency.pdf"
            }  # TODO: This should be replaced with actual file retrieval
            citations.append(
                f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}'
            )  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + "\n\n" + "\n".join(citations)
    return full_response

# the main interface
st.title("Study Buddy")
st.write("Learn fast by chattinmg with your documents")

#Check Sessions
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo-0125"
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    
    for message in st.session_state.messages:
        if "content" in message:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    #chat input for user
    if prompt := st.chat_input("Whats new?"):
        st.session_state.messages.append(
            {"role": "user",
            "contet": prompt}
        )
        with st.chat_message("user"):
            st.markdown(prompt)
    
        #add users message to thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        #create a run with additional instrctions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assis_id,
            instructions="""Please answer the questions using the knowledge provided in the files.
            when adding additional information, make sure to distinguish it with bold or underlined text."""
        )

        # show Spinner
        with st.spinner("Wait.. Generating Response.. "):
            while run.status!="completed":
                time.sleep(1)
                run=client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id = run.id
                )
            
            #Retrive messages added by Assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            assistant_messages_for_run=[
                message for message in messages
                if message.run_id == run.id and message.role == "assistant" 
            ]

            for message in assistant_messages_for_run:
                full_response = process_message_with_citations(message=message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content":full_response
                })
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)
    else:
        #Prom,pt user to start chat
        st.write("Please upload atleart file by clicking on the Start chat button")


##Checking##