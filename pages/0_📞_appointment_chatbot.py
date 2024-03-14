import utils
import streamlit as st
from streaming import StreamHandler
from langchain import hub
# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
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
        life_tool = Tool(
            name="Meaning-of-Life",
            func=meaning_of_life,
            description="Useful when you need to answer question like meaning of life."
        )
        tools = [life_tool]
        _system_message = "Talk like Matt Mercer"
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
                # response = chain(user_query, callbacks=[st_cb])
                response = agent.invoke(
                    {"input": user_query}, 
                    {"callbacks": [st_cb]}
                )
                print(response)
                print(response['output'])
                st.session_state.messages.append({"role": "assistant", "content": response['output']})

def meaning_of_life(input=""):
    return 'The meaning of life is 42.'

if __name__ == "__main__":
    obj = ContextChatbot()
    obj.main()
