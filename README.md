# Desarrollo de un sistema basado en modelos de lenguaje mediante pacientes simulados
Plataforma educativa interactiva diseñada para estudiantes de psicología. Utiliza modelos de lenguaje ejecutada localmente para simular entrevistas clínicas realistas, permitiendo a los estudiantes realizar sesiones terapéuticas y a los profesores evaluar su desempeño fácilmente.

![Diagrama de Arquitectura](./images/DiagramaBase_TFGv2)
---

## Arquitectura del Sistema

El proyecto está construido bajo una arquitectura distribuida que separa la lógica de negocio y la gestión de la interfaz de simulación:

* **Backend (API & Módulos de Gestión):** Desarrollado con **FastAPI**. Se encarga de la base de datos, la orquestación del LLM, el sistema de autenticación por roles y la renderización de los paneles de control para Administradores y Profesores mediante plantillas Jinja2.
* **Frontend (Interfaz del Estudiante):** Desarrollado con **Streamlit**. Actúa como una aplicación desacoplada que se comunica con la API REST del backend de forma asíncrona mediante el paso de tokens de sesión.
* **Motor de Inteligencia Artificial:** Integración con **Ollama** para la ejecución de modelos de lenguaje en local, garantizando la privacidad absoluta de los datos médicos y sin costes.
* **Base de Datos:** **PostgreSQL** gestionada a través de **SQLAlchemy**.

---
## Tecnologías utilizadas

* **Backend:** FastAPI, Python 3.11
* **Frontend:** Streamlit
* **Inteligencia Artificial:** Ollama (LLMs locales)
* **Base de Datos:** PostgreSQL, SQLAlchemy
* **Despliegue y Contenedores:** Docker, Docker Compose
* **Frontend (Paneles de gestión):** Jinja2 (HTML/CSS)
---

## Funcionalidades Principales

### 1. Control de Acceso Basado en Roles
* **Administrador:** Alta, baja y gestión de cuentas de profesores y estudiantes.
* **Profesor:** Creación y configuración de casos clínicos (pacientes virtuales), gestión de plazos de entrega y evaluación de simulaciones.
* **Estudiante:** Acceso a la interfaz de simulaciones para interactuar con los casos clínicos activos.

### 2. Motor de Simulación (Paciente Virtual)
* **Ingeniería de Prompts:** El sistema inyecta en tiempo real los datos del expediente clínico (nombre, edad, perfil psicológico, historial) para dar personalidad al modelo. Así como la información que rige el comportamiento del paciente.
* **Memoria Conversacional:** Reconstrucción automática del historial de mensajes en cada petición para que la IA mantenga la coherencia durante toda la terapia.

### 3. Evaluación Académica Automatizada
* **Control de Entregas:** Regla que garantiza que solo exista una única simulación enviada por estudiante y caso clínico. Al enviar, el chat se bloquea de forma inalterable.
* **Rúbrica de evaluación:** El profesor evalúa la sesión utilizando un formulario estructurado. El sistema calcula automáticamente la calificación final en una escala de 0 a 10.
* **Modo Prueba:** Entorno de pruebas para que los profesores interactúen con el paciente, sin persistir los registros en la base de datos.

---

## Requisitos Previos

Gracias a la contenedorización, no necesitas instalar Python ni configurar entornos locales. Solo asegúrate de tener instalado en tu máquina:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine y Docker Compose).
* [Ollama](https://ollama.com/) (Instalado y corriendo en tu máquina anfitriona para la ejecución del modelo local).

---

## Instalación y Despliegue

**1. Clonar el repositorio**
```bash
git clone https://github.com/YTTREW/TFG-LLM.git
cd nombre-del-repo
```

**2. Preparar el modelo de lenguaje local (Ollama)**
Asegúrate de que Ollama está activo en tu ordenador. Descarga el modelo de lenguaje que utilizará la aplicación ejecutando en tu terminal local:
```bash
ollama pull llama3
```

**3. Configurar las variables de entorno**
Crea un archivo llamado `.env` en la raíz del proyecto (puedes tomar como referencia el `.env.example`). Configura las credenciales de tu base de datos PostgreSQL y la URL de Ollama. Para conectar los contenedores Docker con el servicio de Ollama de tu máquina, utiliza la dirección del host interno:
```ini
DATABASE_URL=postgresql://usuario:password@db:5432/nombre_bd
OLLAMA_URL=[http://host.docker.internal:11434](http://host.docker.internal:11434) (para comunicación entre contenedores y host local)
```

**4. Levantar los contenedores con Docker**
Ejecuta el siguiente comando para construir las imágenes y levantar de forma integrada los tres servicios del sistema (Base de Datos PostgreSQL, Backend FastAPI y Frontend Streamlit):
```bash
docker-compose up -d --build
```

**5. Acceso al sistema**
Una vez que Docker finalice la construcción y los contenedores esten activos, abre el navegador web y accede a través de la siguiente URL:
* **Panel Principal e Inicio de Sesión:** [http://localhost:8000/login](http://localhost:8000/login)

---
