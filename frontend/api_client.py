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

# ---------- NUEVO: Obtener lista de Casos Clínicos ----------
def get_cases():
    url = f"{BASE_URL}/cases"
    res = requests.get(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

# ---------- Obtener lista de chats ----------
def get_chats():
    # FastAPI requiere la barra al final si la ruta es "/"
    url = f"{BASE_URL}/" 
    res = requests.get(url, headers=auth_headers())
    res.raise_for_status()  # Esto lanza el 401 si algo falla
    return res.json()

# ---------- Enviar chat al profesor ----------
def submit_chat(chat_id: int):
    url = f"{BASE_URL}/{chat_id}/submit"
    res = requests.post(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()

# ---------- MODIFICADO: Crear nuevo chat para un caso específico ----------
def create_chat(caso_id: int):
    url = f"{BASE_URL}/"
    res = requests.post(
        url, 
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"caso_id": caso_id} # Enviamos el ID del caso al backend
    )
    res.raise_for_status()
    return res.json()

# ---------- Obtener mensajes de un chat ----------
def get_messages(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.get(url, headers=auth_headers()) 
    res.raise_for_status()
    return res.json()

# ---------- Enviar mensaje al Chat ----------
def send_message(chat_id: int, content: str):
    url = f"{BASE_URL}/{chat_id}/messages"
    res = requests.post(
        url,
        headers={**auth_headers(), "Content-Type": "application/json"},
        json={"content": content}  # Solo enviamos el texto
    )
    res.raise_for_status()
    return res.json() 

# ---------- Borrar un chat ----------
def delete_chat(chat_id: int):
    url = f"{BASE_URL}/{chat_id}"
    res = requests.delete(url, headers=auth_headers())
    res.raise_for_status()
    return res.json()