
import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api/chats" # URL donde esta alojada la API
SESSION = requests.Session() # Sesión para mantener conexiones

#  ---------- Procesa Token ----------
def auth_headers():
    token = st.session_state.get("token")

    if not token or not isinstance(token, str):
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

# ---------- Obtener lista de chats ----------
def get_chats():
    res = requests.get(BASE_URL, headers=auth_headers())
    res.raise_for_status()  # Esto lanza el 401 si algo falla
    return res.json()

# ---------- Crear nuevo chat ----------
def create_chat():
    res = requests.post(BASE_URL, headers=auth_headers())
    res.raise_for_status()
    return res.json()


# ---------- Obtener mensajes de un chat ----------
def get_messages(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.get(url, headers=auth_headers()) 
    res.raise_for_status()
    return res.json()

# ---------- Guardar mensaje en un chat ----------
def save_message(chat_id: int, role: str, content: str):
    url = f"{BASE_URL}/{chat_id}/messages"
    res = requests.post(
        url,
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"role": role, "content": content}  
    )
    res.raise_for_status()
    return res.json()

# ---------- Borrar un chat ----------
def delete_chat(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.delete(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

