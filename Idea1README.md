### PROYECTO FINAL PROPUESTO — ASISTENTE DE DUNGEONS & DRAGONS
Aplicación Fullstack con IA integrada

## DESCRIPCIÓN GENERAL
El proyecto consiste en crear un asistente inteligente para jugadores y Dungeon Masters de Dungeons & Dragons (basado en el SRD 5.1, que es de licencia libre).
La aplicación permite a los usuarios consultar reglas, buscar hechizos, entender condiciones, resolver dudas de combate y gestionar información básica de personajes.
El agente de IA utiliza RAG para responder preguntas basadas en documentos del SRD y herramientas personalizadas para cálculos, búsquedas, ayudar en la creación de personajes y tiradas de dados.

## OBJETIVO PRINCIPAL
Construir una aplicación fullstack donde la IA sea el núcleo del producto.

El agente debe ser capaz de:

    * Explicar reglas de D&D (acciones, combate, condiciones, hechizos).

    * Buscar hechizos por nivel, clase o escuela.

    * Resolver dudas de mecánicas usando RAG.

    * Realizar tiradas de dados mediante tools.

    * Consultar información almacenada en la base de datos.

## FUNCIONALIDADES PRINCIPALES

* Autenticación JWT (registro, login, rutas protegidas).

* CRUD de personajes o “favoritos” (hechizos, reglas, notas).

* Buscador de hechizos y condiciones.

* Chat con IA integrado en el frontend.

* RAG con documentos del SRD 5.1 y contenido propio.

* Tools del agente:

    Tiradas de dados

    Búsqueda de hechizos

    Búsqueda de condiciones

    Consulta a la base de datos

* Workflow N8N que se activa cuando un usuario crea un personaje o guarda un hechizo favorito.

* Diseño responsive.

## BACKEND (FastAPI + PostgreSQL)
Tecnologías:

    FastAPI

    Pydantic v2

    PostgreSQL

    LangChain + LangGraph

    ChromaDB

    JWT

    N8N (webhook)

Tablas mínimas:

    usuarios

    personajes (o favoritos)

    hechizos (importados del SRD)

Relaciones:

    Un usuario puede tener muchos personajes o favoritos.

    Los hechizos pueden consultarse desde la base de datos o desde el RAG.

Endpoints mínimos:

    /auth/register

    /auth/login

    /auth/me

    /personajes (GET, POST, PUT, DELETE)

    /hechizos (GET)

    /api/chat (POST)

    /api/chat/history/{id} (GET)

    /webhook/n8n (POST)

# Agente IA:

Construido con LangGraph.

* Debe tener al menos 2 tools:

    Tool RAG (consulta a ChromaDB)

    Tool tiradas de dados

    Tool búsqueda de hechizos

* Memoria conversacional persistente.

* Cita fuentes cuando usa RAG.

* Maneja errores y casos límite.

Documentos propuestos para RAG (mínimo 5):

    Reglas básicas del SRD 5.1

    Reglas de Combate

    Condiciones (envenenado, cegado, agarrado, etc.)

    Hechizos del SRD (resumen)

    Clases y características (resumen)

    Enemigos

### FRONTEND (React + Vite)
Tecnologías:

    React 18

    React Router v6

    Context API (usuario autenticado)

    Formularios con validación

    Axios o fetch

    Diseño responsive

Rutas mínimas:

    /login

    /register

    /personajes

    /hechizos

    /chat

    /perfil

Componentes clave:

    Formulario de login/registro

    Lista de hechizos

    Detalle de hechizo

    Lista de personajes

    Formulario para crear personaje

    Chat con IA

    Header con estado de sesión

Estados a manejar:

    loading

    error

    empty

    success

## AUTOMATIZACIÓN N8N
Workflow mínimo:

    Trigger: Webhook desde FastAPI cuando un usuario crea un personaje o guarda un hechizo favorito.

    IF: Si el personaje es de cierto nivel o clase, o si el hechizo pertenece a una escuela concreta.

    Acción: Enviar email, registrar evento o guardar log.

    Exportar JSON al repositorio.

## DESPLIEGUE

    Backend: Railway / Render / Fly.io

    Base de datos: Railway / Neon / Supabase

    Frontend: Netlify / Vercel

    Variables de entorno en .env y .env.example

    Comunicación HTTPS entre front y back

    Agente IA funcionando en producción


## ROADMAP DE DESARROLLO (RESUMIDO)
Día 1: Diseño BD + estructura backend
Día 2: Autenticación + CRUD personajes
Día 3: Endpoints de hechizos + endpoints IA
Día 4: Agente LangGraph + RAG + tools
Día 5: Frontend base + login + personajes
Día 6: Chat IA + buscador de hechizos
Día 7: N8N + despliegue
Día 8: Documentación + pruebas + presentación