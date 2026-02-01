from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama

class Chatbot:
    def __init__(self):
        self.llm = ChatOllama(model="llama3", temperature=0.7)
        self.history = []

    def load_history(self, messages):
        self.history = []
        for msg in messages:
            if msg["role"] == "user":
                self.history.append(HumanMessage(content=msg["content"]))
            else:
                self.history.append(AIMessage(content=msg["content"]))

    def ask(self, text: str) -> str:
        self.history.append(HumanMessage(content=text))
        response = self.llm.invoke(self.history)
        self.history.append(AIMessage(content=response.content))
        return response.content
