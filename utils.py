import os
import random
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import Tool
from langchain.pydantic_v1 import BaseModel, Field
# from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.tools import tool, BaseTool
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Type
from pydantic import BaseModel

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

def get_today_date_time(input=""):
    now = dt.datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    local_tzname = local_tz.tzname(local_now)
    result = f"The date and time of today is {now}, {now.strftime('%A')}, {local_now}, {local_tz}, {local_tzname}"
    print(result)
    return result

get_today_date_time_tool = Tool(
    name="Get-current-date-and-time",
    func=get_today_date_time,
    description = (
        "Useful when you need to answer question about current date time information."
    )
)


def get_day_of_date_time(input=""):
    format = "%Y-%m-%d"
    date = dt.datetime.strptime(input, format)
    local_date = date.astimezone()
    local_tz = local_date.tzinfo
    local_tzname = local_tz.tzname(local_date)
    result = f"The date and time of date {date}, {date.strftime('%A')}, {local_date}, {local_tz}, {local_tzname}"
    print(result)
    return result

get_day_of_date_time_tool = Tool(
    name="Get-day-of-date-and-time",
    func=get_day_of_date_time,
    description = (
        "Useful when you know the day of certain date."
        "Input is a string of date in the format of YYYY-MM-DD"
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
            print(event)
            id = event["id"]
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event["summary"]
            # print(start, event["summary"])
            # results.append(", ".join([id, start, event["summary"]]))
            results.append({
                "id": id,
                "start_time": start,
                "summary": summary,
            })
        print(results)
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
        "The response is a list of events, each event contains 3 attributes, id, start_time and summary"
    )
)


class GetDateTimeTool(BaseTool):
    name = "get-current-date-time"
    description = """
        use this tool when need to get current year, date, time, or timezone info.
    """
    def _run(
        self, 
    ) -> str:
        now = dt.datetime.now()
        local_now = now.astimezone()
        local_tz = local_now.tzinfo
        local_tzname = local_tz.tzname(local_now)
        result = f"The date and time of today is {now}, {now.strftime('%A')}, {local_now}, {local_tz}, {local_tzname}"
        print(result)
        return result

    async def _arun(
        self, query: str,
    ) -> str:
        raise NotImplementedError("custom_search does not support async")

getDateTimeTool = GetDateTimeTool()


class CalendarInput(BaseModel):
    summary: str = Field(description="summary of the event")
    start_time: str = Field(description="event start time, in the format of YYYY-MM-DD HH:MM:SS")
    end_time: str = Field(description="event end time, in the format of YYYY-MM-DD HH:MM:SS")

class SetGoogleCalendarTool(BaseTool):
    name = "set-google-calendar"
    description = """
        use this tool when need to schedule a new event for the user.
        To use this tool, you need to provide all 3 following parameters:
        [summary, start_time, and end_time]
        For each parameter, below is the description
        summary: summary of the event
        start_time: event start time, in the format of YYYY-MM-DD HH:MM:SS
        end_time: event end time, in the format of YYYY-MM-DD HH:MM:SS
    """
    args_schema: Type[BaseModel] = CalendarInput

    def _run(
        self, 
        summary: str = None,
        start_time: str = None,
        end_time: str = None,
    ) -> str:
        try:
            print(summary)
            print(start_time)
            print(end_time)
            start_time = start_time.replace(" ", "T")
            start_time = start_time + "-04:00"
            end_time = end_time.replace(" ", "T")
            end_time = end_time + "-04:00"
            service = build("calendar", "v3", credentials=auth_google())
            event = {
                "summary": summary,
                "location": "Online meeting",
                "description": "Some more details on this event",
                "start": {
                    "dateTime": start_time,
                    "timeZone": "US/Eastern"
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": "US/Eastern"
                }
            }
            event = service.events().insert(calendarId="primary", body=event).execute()
            print(event)     
        except HttpError as error:
            print(f"An error occurred: {error}")   
        return "LangChain"

    async def _arun(
        self, query: str,
    ) -> str:
        raise NotImplementedError("custom_search does not support async")

setGoogleCalendarTool = SetGoogleCalendarTool()


class CalendarIdInput(BaseModel):
    id: str = Field(description="id of the event")

class CancelGoogleCalendarTool(BaseTool):
    name = "cancel-google-calendar"
    description = """
        use this tool when need to cancel or delete an event for the user.
        To use this tool, you need to provide the parameters:
        id: the event id
    """
    args_schema: Type[BaseModel] = CalendarIdInput

    def _run(
        self, 
        id: str = None,
    ) -> str:
        try:
            print(id)
            service = build("calendar", "v3", credentials=auth_google())
            service.events().delete(calendarId="primary", eventId=id).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")   
        return "LangChain"

    async def _arun(
        self, query: str,
    ) -> str:
        raise NotImplementedError("custom_search does not support async")

cancelGoogleCalendarTool = CancelGoogleCalendarTool()

def set_google_events(start_time, end_time, summary):
    try:
        service = build("calendar", "v3", credentials=auth_google())
        event = {
            "summary": summary,
            "location": "Online meeting",
            "description": "Some more details on this event",
            "start": {
                "dateTime": start_time,
                "timeZone": "US/Eastern"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "US/Eastern"
            }
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        print(event)
    except HttpError as error:
        print(f"An error occurred: {error}")

def set_visits(input=""):
    visits = ""
    with open("visits.txt", "a") as f:
        f.write("\n")
        f.write(input)
    return

set_visits_tool = Tool(
    name="Set-new-visit",
    func=set_google_events,
    description = (
        "Useful when user wants to schedule a new event"
        "To use this tool the input should provide below parameters:"
        "summary - summary of the event"
        "start_time - event start time, in the format like 2024-03-15T08:00:00-04:00"
        "end_time - event end time, in the format like 2024-03-15T10:00:00-04:00"
    )
)
