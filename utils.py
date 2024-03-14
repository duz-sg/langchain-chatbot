import os
import random
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import Tool
from datetime import datetime

#decorator
def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):

        # to clear chat history after swtching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass

        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)
    return execute

def display_msg(msg, author):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)

def configure_openai_api_key():
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY') or st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        value=st.session_state['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in st.session_state else '',
        placeholder="sk-..."
        )
    if openai_api_key:
        st.session_state['OPENAI_API_KEY'] = openai_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.stop()
    return openai_api_key

def meaning_of_life(input=""):
    return 'The meaning of life is 42.'

life_tool = Tool(
    name="Meaning-of-Life",
    func=meaning_of_life,
    description = (
        "Useful when you need to answer question about meaning of life."
        "Should only be used to answer question about meaning of life."
    )
)

def get_visits(input=""):
    visits = ""
    with open("visits.txt", "r") as f:
        visits = f.readlines()
    return visits

get_visits_tool = Tool(
    name="Get-current-visits",
    func=get_visits,
    description = (
        "Useful when you need to answer question about user's visit plans for the future."
    )
)

def set_visits(input=""):
    visits = ""
    with open("visits.txt", "a") as f:
        f.write("\n")
        f.write(input)
    return

set_visits_tool = Tool(
    name="Set-new-visit",
    func=set_visits,
    description = (
        "Useful when user wants to schedule a new event"
        "Input is the event in the format as below:"
        "{YYYY-MM-DD, Start time - Finish time, Evnet title}"
    )
)

def get_date_time(input=""):
    now = datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    local_tzname = local_tz.tzname(local_now)
    result = f"The date and time of today is {now}, {now.strftime('%A')}, {local_now}, {local_tz}, {local_tzname}"
    print(result)
    return result

get_date_time_tool = Tool(
    name="Get-current-date-and-time",
    func=get_date_time,
    description = (
        "Useful when you need to answer question about current date time information."
        # "Should only be used to answer question about meaning of life."
    )
)