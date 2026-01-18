from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama

class Chatbot:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3",
            temperature=0.7
        )
        self.history = []

    def ask(self, user_message: str) -> str:
        self.history.append(HumanMessage(content=user_message))

        response = self.llm.invoke(self.history)

        # 🔴 CLAVE: response es un AIMessage
        text = response.content

        self.history.append(AIMessage(content=text))

        return text


