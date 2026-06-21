# Simulador de Pacientes Virtuales con IA para Psicología Clínica 🧠🤖

Plataforma educativa interactiva diseñada para estudiantes de psicología y profesionales de la salud. Utiliza Inteligencia Artificial (Modelos de Lenguaje Grande - LLMs) ejecutada localmente para simular entrevistas clínicas realistas, permitiendo a los estudiantes practicar, y a los profesores evaluar su desempeño de forma estandarizada.

---

## 🚀 Arquitectura del Sistema

El proyecto está construido bajo una arquitectura distribuida que separa la lógica de negocio y la gestión académica de la interfaz de simulación:

* **Backend (API & Paneles de Gestión):** Desarrollado con **FastAPI**. Se encarga de la base de datos, la orquestación del LLM, el sistema de autenticación (RBAC) y la renderización de los paneles de control para Administradores y Profesores mediante plantillas Jinja2.
* **Frontend (Interfaz del Estudiante):** Desarrollado con **Streamlit**. Actúa como una aplicación desacoplada que se comunica con la API REST del backend de forma asíncrona mediante el paso de tokens de sesión.
* **Motor de Inteligencia Artificial:** Integración con **Ollama** para la ejecución de modelos de lenguaje en local, garantizando la privacidad absoluta de los datos médicos y la nula latencia con servicios externos.
* **Base de Datos:** **PostgreSQL** gestionada a través del ORM **SQLAlchemy**.

---

## ✨ Funcionalidades Principales

### 1. Control de Acceso Basado en Roles (RBAC)
* **Administrador:** Alta, baja y gestión de cuentas de profesores y estudiantes.
* **Profesor:** Creación y configuración de casos clínicos (pacientes virtuales), gestión de plazos de entrega y evaluación de simulaciones.
* **Estudiante:** Acceso al portal de simulaciones para interactuar con los casos clínicos activos.

### 2. Motor de Simulación (IA Contextual)
* **Ingeniería de Prompts Dinámica:** El sistema inyecta en tiempo real los datos del expediente clínico (nombre, edad, perfil psicológico, historial) para dar personalidad al modelo.
* **Memoria Conversacional:** Reconstrucción automática del historial de mensajes en cada petición para que la IA mantenga la coherencia durante toda la terapia (superando la limitación *stateless* de los LLMs).

### 3. Evaluación Académica Automatizada
* **Control de Entregas Estricto:** Regla de exclusión mutua que garantiza que solo exista una única simulación activa/enviada por estudiante y caso clínico. Al enviar, el chat se bloquea de forma inalterable.
* **Rúbrica de 16 Ítems:** El profesor evalúa la sesión utilizando un formulario estructurado. El sistema calcula dinámicamente la media, pondera el resultado y lo escala a una calificación estándar de 0 a 10.
* **Modo *Sandbox* (Pruebas):** Entorno de pruebas efímero para que los profesores interactúen con el modelo al vuelo antes de publicar un caso, sin generar registros "basura" en la base de datos.

---

## 🛠️ Requisitos Previos

Asegúrate de tener instalado en tu máquina:
* [Python 3.9+](https://www.python.org/downloads/)
* [PostgreSQL](https://www.postgresql.org/download/)
* [Ollama](https://ollama.com/) (con el modelo deseado descargado, ej: `ollama run llama3`)

---

## ⚙️ Instalación y Despliegue

**1. Clonar el repositorio**
```bash
git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
cd nombre-del-repo
