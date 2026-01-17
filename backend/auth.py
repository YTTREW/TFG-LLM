def authenticate_user(username: str, password: str):
    users = {
        "profesor": {
            "password": "prof123",
            "role": "profesor"
        },
        "estudiante": {
            "password": "estu123",
            "role": "estudiante"
        }
    }

    user = users.get(username)

    if user and user["password"] == password:
        return user["role"]

    return None
