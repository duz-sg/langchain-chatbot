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
        self.openai_model = "gpt-3.5-turbo"
    
    @st.cache_resource
    def setup_chain(_self):
        # memory = ConversationBufferMemory(return_messages=True)
        llm = ChatOpenAI(model=_self.openai_model, temperature=0.2)
        memory = ConversationBufferMemory(
            llm=llm, 
            memory_key="memory", 
            return_messages=True
            )

        tools = [
            utils.life_tool, 
            utils.get_visits_tool, 
            utils.set_visits_tool,
            utils.get_date_time_tool,
            TavilySearchResults(max_results=1)]
        _system_message ="""
        Assistant is a large language model.
        Assistant is honest and polite, and is able to help user to make appointments.
        However, assistant does not know anything about the event, before scheduling for
        the user, the assistant needs to alway ask user about title of the event.
        All day appointment means the user is busy all day, and cannot arrange more events.
        New events should only be put between 8:00 and 17:00.
        Unless user specifies, each new event should take 1 hour.
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
