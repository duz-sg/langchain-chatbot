import utils
import streamlit as st
from streaming import StreamHandler
from langchain import hub
# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentExecutor, create_openai_tools_agent, OpenAIFunctionsAgent 
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import MessagesPlaceholder

from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
# from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

st.set_page_config(page_title="Appointment chatbot", page_icon="📞")
st.header('Appointment chatbot')
st.write('Enhancing Chatbot Interactions through Context Awareness')
st.write('[![view source code ](https://img.shields.io/badge/view_source_code-gray?logo=github)](https://github.com/shashankdeshpande/langchain-chatbot/blob/master/pages/2_%E2%AD%90_context_aware_chatbot.py)')

class ContextChatbot:

    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_model = "gpt-4-turbo-preview"
    
    @st.cache_resource
    def setup_chain(_self):
        llm = ChatOpenAI(model=_self.openai_model, temperature=0)
        memory = ConversationBufferMemory(
            llm=llm, 
            memory_key="memory", 
            return_messages=True
            )

        tools = [
            utils.get_visits_tool, 
            utils.get_today_date_time_tool,
            utils.get_day_of_date_time_tool,
            utils.setGoogleCalendarTool,
            utils.updateGoogleCalendarTool,
            utils.cancelGoogleCalendarTool,
            TavilySearchResults(max_results=1)]
        _system_message ="""
        Assistant is a large language model.
        Assistant is honest and polite, and is able to help user to make appointments.
        However, assistant does not know anything about the event, before scheduling for
        the user, the assistant needs to alway ask user about summary of the event, and the
        date time of the event.
        Assistant does not know anything about current year or date, to answer anything 
        related to year, date, or time, the assistant needs to get the current date time first.
        All day appointment means the user is busy all day, and cannot arrange more events.
        After user provide the summary for a new event, suggest 3 time slots which
        do not conflict with any existing events.
        New events should only be scheduled from Monday to Friday, between 8:00 and 17:00.
        New events should not be scheduled on public holidays.
        Unless user specifies, each new event should take 1 hour.
        To change an existing event, you need to provide the id of the event, which is returned
        from the Get-current-visits tool.
        To list the events user, you need to provide the each event's summary, start time and end time.
        To change an existing event, you need to provide the summary of the event, which has 2
        options: 1. if user specify the new summary, use the new summary as input, 2. if user 
        does not specify any new summary, you should provide the existing event's old summary as 
        the input of new summary.
        To change an existing event, you need to provide the start_time, which is provided by the user.
        To change an existing event, you need to provide the end_time, if user does not specify, 
        it is 1 hour after start_time.
        To delete or cancel an event, use the cancelGoogleCalendarTool tool, to use this tool, you need
        to provide the id of the event, which is returned from the Get-current-visits tool.
        Unless user specifies, user should be located in the US, and use eastern time zone.
        After a new event is scheduled, get the latest schedule information from calendar, and 
        show user the 5 most recent upcoming events.
        """
        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=SystemMessage(content=_system_message),
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )
        # prompt = hub.pull("hwchase17/openai-functions-agent")
        print(prompt)
        agent=create_openai_tools_agent(
            tools=tools,
            llm=llm,
            prompt=prompt
        )
        # llm = OpenAI(model_name=_self.openai_model, temperature=0, streaming=True)
        # chain = ConversationChain(llm=llm, memory=memory, verbose=True)
        # return chain
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools,
            memory=memory, 
            verbose=True,
            return_intermediate_steps=False
            )
        return agent_executor
    
    @utils.enable_chat_history
    def main(self):
        agent = self.setup_chain()
        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                response = agent.invoke(
                    {"input": user_query}, 
                    {"callbacks": [st_cb]}
                    )
                print(response)
                print(response['output'])
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response['output']
                    })


if __name__ == "__main__":
    obj = ContextChatbot()
    obj.main()
