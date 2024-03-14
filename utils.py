import os
import random
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import Tool
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

def get_date_time(input=""):
    now = dt.datetime.now()
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

def auth_google():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_google_events(input=""):
    print(input)
    try:
        service = build("calendar", "v3", credentials=auth_google())
        # Call the Calendar API
        now = dt.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            print("No upcoming events found.")
            return

        results = []
        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            results.append(", ".join([start, event["summary"]]))
        return results
    except HttpError as error:
        print(f"An error occurred: {error}")

def get_visits(input=""):
    visits = ""
    with open("visits.txt", "r") as f:
        visits = f.readlines()
    return visits

get_visits_tool = Tool(
    name="Get-current-visits",
    func=get_google_events,
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
