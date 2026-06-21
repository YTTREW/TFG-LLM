# Simulador de Pacientes Virtuales con IA para Psicología Clínica 🧠🤖
Plataforma educativa interactiva diseñada para estudiantes de psicología. Utiliza Inteligencia Artificial (Modelos de Lenguaje Grande - LLMs) ejecutada localmente para simular entrevistas clínicas realistas, permitiendo a los estudiantes practicar, y a los profesores evaluar su desempeño fácilmente.

---

## 🚀 Arquitectura del Sistema

El proyecto está construido bajo una arquitectura distribuida que separa la lógica de negocio y la gestión de la interfaz de simulación:

* **Backend (API & Módulos de Gestión):** Desarrollado con **FastAPI**. Se encarga de la base de datos, la orquestación del LLM, el sistema de autenticación por roles y la renderización de los paneles de control para Administradores y Profesores mediante plantillas Jinja2.
* **Frontend (Interfaz del Estudiante):** Desarrollado con **Streamlit**. Actúa como una aplicación desacoplada que se comunica con la API REST del backend de forma asíncrona mediante el paso de tokens de sesión.
* **Motor de Inteligencia Artificial:** Integración con **Ollama** para la ejecución de modelos de lenguaje en local, garantizando la privacidad absoluta de los datos médicos y sin costes.
* **Base de Datos:** **PostgreSQL** gestionada a través de **SQLAlchemy**.

---

## ✨ Funcionalidades Principales

### 1. Control de Acceso Basado en Roles (RBAC)
* **Administrador:** Alta, baja y gestión de cuentas de profesores y estudiantes.
* **Profesor:** Creación y configuración de casos clínicos (pacientes virtuales), gestión de plazos de entrega y evaluación de simulaciones.
* **Estudiante:** Acceso a la interfaz de simulaciones para interactuar con los casos clínicos activos.

### 2. Motor de Simulación (Paciente Virtual)
* **Ingeniería de Prompts:** El sistema inyecta en tiempo real los datos del expediente clínico (nombre, edad, perfil psicológico, historial) para dar personalidad al modelo. Así como la información que rige el comportamiento del paciente.
* **Memoria Conversacional:** Reconstrucción automática del historial de mensajes en cada petición para que la IA mantenga la coherencia durante toda la terapia.

### 3. Evaluación Académica Automatizada
* **Control de Entregas Estricto:** Regla que garantiza que solo exista una única simulación enviada por estudiante y caso clínico. Al enviar, el chat se bloquea de forma inalterable.
* **Rúbrica de evaluación:** El profesor evalúa la sesión utilizando un formulario estructurado. El sistema calcula dinámicamente la media y se obtiene una calificación estándar de 0 a 10.
* **Modo Prueba:** Entorno de pruebas para que los profesores interactúen con el paciente, sin generar registros  en la base de datos.

---

## 🛠️ Requisitos Previos

Gracias a la contenedorización, no necesitas instalar Python ni configurar entornos locales. Solo asegúrate de tener instalado en tu máquina:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o Docker Engine y Docker Compose).
* [Ollama](https://ollama.com/) (Instalado y corriendo en tu máquina anfitriona para la ejecución del modelo local).

---

## ⚙️ Instalación y Despliegue

**1. Clonar el repositorio**
```bash
git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
cd nombre-del-repo
```

**2. Preparar el modelo de lenguaje local (Ollama)**
Asegúrate de que Ollama está activo en tu ordenador. Descarga el modelo de lenguaje que utilizará la aplicación ejecutando en tu terminal local:
```bash
ollama pull llama3
```

**3. Configurar las variables de entorno**
Crea un archivo llamado `.env` en la raíz del proyecto (puedes tomar como referencia un `.env.example`). Configura las credenciales de tu base de datos PostgreSQL y la URL de Ollama. Para conectar los contenedores Docker con el servicio de Ollama de tu máquina, utiliza la dirección del host interno:
```ini
DATABASE_URL=postgresql://usuario:password@db:5432/nombre_bd
OLLAMA_URL=[http://host.docker.internal:11434](http://host.docker.internal:11434)
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
