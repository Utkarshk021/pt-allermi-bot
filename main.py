import openai
import streamlit as st
import time

assistant_id = st.secrets["ASSISTANT_KEY"]

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "buttons_shown" not in st.session_state:
    st.session_state.buttons_shown = False
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

st.set_page_config(page_title="Bloom", page_icon=":speech_balloon:")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Sidebar for user input
st.sidebar.title("Tell us about your allergies")

symptoms = st.sidebar.selectbox("What are your typical allergy symptoms?", 
                                ["Runny nose", "Sneezing", "Congestion", "Itchy Eyes"])
frequency = st.sidebar.selectbox("How often do you experience these symptoms?", 
                                 ["Daily", "Seasonally", "Occasionally"])
severity = st.sidebar.selectbox("Are you atleast 18 years old?", 
                                ["Yes", "No"])
state = st.sidebar.selectbox("Which state do you currently live in?", 
                                ["California", "New York", "Alaska", "North Carolina", "Washington", "Other"])
situations = st.sidebar.text_input("Enter your email address. (optional)")

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.symptoms = symptoms
    st.session_state.frequency = frequency
    st.session_state.severity = severity
    st.session_state.situations = situations
    st.session_state.state = state
    st.session_state.buttons_shown = False  # Reset buttons_shown when starting a new chat
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.title("I am Bloom! Your AI Assistant")
st.write("Welcome! My name is Bloom- I'm here to help you get best allergy treatment.")

if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.buttons_shown = False  # Reset buttons_shown on exiting chat

def typing_effect(text):
    for char in text:
        yield char
        time.sleep(0.008)

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial assistant message
    if not st.session_state.messages:
        initial_message = f"Thanks for sharing your allergy information about your :red[{st.session_state.symptoms}.] " \
                          f"We understand how frustrating allergies can be, and are here to to manage your allergies and get relief! " \

        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(initial_message))

        summary_message = "Based on your inputs, :green[You're eligible for a Custom Rx Nasal Spray Kit.] Allermi use custom combinations of clinically-proven ingredients to address ALL your symptoms in one simple spray."
        st.session_state.messages.append({"role": "assistant", "content": summary_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(summary_message))

        allermi_message = "Your kit contains a :blue[one-month supply] of your custom :blue[Rx Super Spray] and :blue[Salinity Spray] made to address your specific symptoms and to help moisturize your nasal passage for maximum relief. What questions do you have for me that I can help you with? "
        st.session_state.messages.append({"role": "assistant", "content": allermi_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(allermi_message))


    # Add predefined buttons only at the start
    if not st.session_state.buttons_shown:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("How does Allermi cure my allergies?"):
                st.session_state.prompt = "How does Allermi cure my allergies?"
                st.session_state.buttons_shown = True
            if st.button("How can I book an appointment?"):
                st.session_state.prompt = "How can I book an appointment?"
                st.session_state.buttons_shown = True
            if st.button("Does Allermi accept health insurance?"):
                st.session_state.prompt = "Does Allermi accept health insurance?"
                st.session_state.buttons_shown = True
        with col2:
            if st.button("What formulae do you use to cure allergies?"):
                st.session_state.prompt = "What formulae do you use to cure allergies?"
                st.session_state.buttons_shown = True
            if st.button("What are the active ingredients in super spray?"):
                st.session_state.prompt = "What are the active ingredients in super spray?"
                st.session_state.buttons_shown = True
            if st.button("Am I able to request a formula change?"):
                st.session_state.prompt = "Am I able to request a formula change?"
                st.session_state.buttons_shown = True

    if st.session_state.prompt:
        st.session_state.messages.append({"role": "user", "content": st.session_state.prompt})
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=st.session_state.prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))
        
        st.session_state.prompt = ""

    # User input
    if user_input := st.chat_input("How can I help you with your allergies?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))

else:
    st.write("Please provide your allergy information in the sidebar and click 'Start Chat' to begin.")
