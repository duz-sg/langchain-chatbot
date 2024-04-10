# Chatbot Implementations with Langchain + Streamlit

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://langchain-chatbot.streamlit.app/)

Langchain is a powerful framework designed to streamline the development of applications using Language Models (LLMs). \
It provides a comprehensive integration of various components, simplifying the process of assembling them to create robust applications.

## 💬 Sample chatbot use cases
Here are a few examples of chatbot implementations using Langchain and Streamlit:
-  **Appointment Chatbot** \
  A chatbot that allow you to interact with your Google Calendar. This function requires Google Calendar API credential setup.

-  **Basic Chatbot** \
  Engage in interactive conversations with the LLM.

- **Context aware chatbot** \
  A chatbot that remembers previous conversations and provides responses accordingly.

-  **Chatbot with Internet Access** \
  An internet-enabled chatbot capable of answering user queries about recent events.

-  **Chat with your documents** \
  Empower the chatbot with the ability to access custom documents, enabling it to provide answers to user queries based on the referenced information.

## <img src="https://streamlit.io/images/brand/streamlit-mark-color.png" width="40" height="22"> Streamlit App
Created a multi-page streamlit app containing all sample chatbot use cases. \
You can access this app through this link: [langchain-chatbot.streamlit.app](https://langchain-chatbot.streamlit.app)

## 🖥️ Running locally
Prepare a .env file to pass the API keys
```
OPENAI_API_KEY="sk-xxxxxx"
TAVILY_API_KEY="tvly-xxxxxx" (Optional)
```

Enable Interaction with Google API in appointment chatbot (Optional)
Setup your Google Developer Account for Google Calendar, download the credentials json to the root folder and name it credentials.json

```shell
# Run main streamlit app
$ streamlit run Home.py
```

## 💁 Contributing
Planning to add more chatbot examples over time. PRs are welcome.
