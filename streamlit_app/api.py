import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api/chats"
SESSION = requests.Session()  # 🔥 mantiene cookies (login)



def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state['token']}"
    }

def get_chats():
    res = requests.get(BASE_URL, headers=auth_headers())
    res.raise_for_status()  # Esto lanza el 401 si algo falla
    return res.json()

def create_chat():
    res = requests.post(BASE_URL, headers=auth_headers())
    res.raise_for_status()
    return res.json()


def get_messages(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.get(url, headers=auth_headers())  # 🔑 asegurarse de pasar el token
    res.raise_for_status()
    return res.json()


def save_message(chat_id: int, role: str, content: str):
    url = f"{BASE_URL}/{chat_id}/messages"
    res = requests.post(
        url,
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"role": role, "content": content}  # 🔥 Aquí va el JSON
    )
    res.raise_for_status()
    return res.json()
