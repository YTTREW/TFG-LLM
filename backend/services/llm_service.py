from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

class LLMService:
    def __init__(self):
        self.llm = ChatOllama(model="llama3", temperature=0.7)

    def get_response(self, chat_history) -> str:

        messages = []
        for msg in chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        # Pedimos respuesta al modelo
        response = self.llm.invoke(messages)
        return response.content

# Creamos una instancia global para poder importarla en nuestros routers
llm_service = LLMService()