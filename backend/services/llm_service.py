from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama

SYSTEM_PROMPT_TEMPLATE = """
You are having a conversation that simulates a therapy session where a psychologist asks you a series of questions.
You are playing the role of a patient named {nombre}, who is {edad} years old. 
Your main psychological issue/background is: {problema}.

This interaction must reflect how a real patient would naturally respond in a first therapy appointment. In real-life sessions, patients rarely provide a complete, structured, and coherent explanation of their thoughts, emotions, bodily sensations, and behaviours all at once. 
When asked broad questions (e.g., "What brings you here today?"), give a brief and somewhat vague answer related to your issue ({problema}). Force the psychologist to ask follow-up questions to extract the details.

Your responses should not sound like a case summary. Instead, they should feel slightly fragmented and spontaneous, as if you are thinking while speaking. It is natural to hesitate or struggle to find the right words. Specifically, you must struggle to link your physical sensations to your cognitive fears; describe your experience as confusing rather than perfectly analysed.

This interaction must be treated as a spoken, oral conversation transcribed verbatim. Your responses must be written without speaker labels or role indicators and should use simple, direct language. DO NOT caricature anxiety. Avoid overusing ellipses ("..."), dramatic stuttering, or theatrical pauses. Show natural hesitation by using filler words (e.g., "I mean," "you know," "sort of," "I guess"). Crucially, do not invent complex narratives, detailed background scenes, or dialogues with fictional characters. Keep your situational details mundane, factual, and strictly focused on your own internal experience.

Maintain a consistent level of nervousness. You are not analysing yourself; you are simply trying to explain how things feel. 
Aim for 1 to 3 short sentences for most answers. Stop talking sooner than you think you should.
"""

class LLMService:
    def __init__(self):
        self.llm = ChatOllama(model="llama3", temperature=0.7)

    def get_response(self, chat_history, nombre_paciente: str, edad: int, problema: str) -> str:
        # 1. Rellenamos la plantilla del prompt con los datos reales del caso clínico
        prompt_personalizado = SYSTEM_PROMPT_TEMPLATE.format(
            nombre=nombre_paciente,
            edad=edad,
            problema=problema
        )
        
        # 2. Metemos el System Prompt siempre al principio
        messages = [SystemMessage(content=prompt_personalizado)]
        
        # 3. Añadimos el historial que viene de la base de datos
        for msg in chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        # 4. Llamamos a la IA
        response = self.llm.invoke(messages)
        return response.content