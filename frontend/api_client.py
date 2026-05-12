import os
import requests
import streamlit as st

BACKEND_HOST = os.getenv("BACKEND_URL", "http://localhost:8000")

BASE_URL = f"{BACKEND_HOST}/api/chats"

SESSION = requests.Session()

# Procesa Token
def auth_headers():
    token = st.session_state.get("token")

    if not token or not isinstance(token, str):
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

# Obtener lista de Casos Clínicos
def get_cases():
    url = f"{BASE_URL}/cases"
    res = requests.get(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

# Obtener lista de chats
def get_chats():
    url = f"{BASE_URL}/" 
    res = requests.get(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

# Enviar chat al profesor
def submit_chat(chat_id: int):
    url = f"{BASE_URL}/{chat_id}/submit"
    res = requests.post(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

# Crear nuevo chat
def create_chat(clinical_case_id: int):
    url = f"{BASE_URL}/"
    res = requests.post(
        url, 
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"clinical_case_id": clinical_case_id} 
    )
    res.raise_for_status()
    return res.json()

# Obtener mensajes de un chat
def get_messages(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.get(url, headers=auth_headers()) 
    res.raise_for_status()
    return res.json()

# Enviar mensaje al Chat
def send_message(chat_id: int, content: str):
    url = f"{BASE_URL}/{chat_id}/messages"
    res = requests.post(
        url,
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"content": content} 
    ) 
    res.raise_for_status()
    return res.json() 

# Borrar un chat
def delete_chat(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.delete(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()