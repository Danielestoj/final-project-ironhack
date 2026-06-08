## PROYECTO FINAL PROPUESTO — MINI INFOJOBS / LINKEDIN
Aplicación Fullstack con IA integrada

## DESCRIPCIÓN GENERAL
El proyecto consiste en crear una plataforma web tipo InfoJobs/LinkedIn en versión minimalista en donde son las empresas las que publican ofertas y contactan con los usuarios que cumplan los requisitos. Los usuarios pueden registrarse, iniciar sesión, ver ofertas de empleo, crear ofertas (si son empresas), aplicar a ofertas y usar un chat con IA que actúa como asesor laboral. La IA utiliza RAG para recomendar candidatos, mejorar el CV o dar consejos laborales basados en documentos preindexados.

## OBJETIVO PRINCIPAL
Construir una aplicación fullstack donde la IA sea el núcleo del producto, no un añadido.
El agente debe ser capaz de:

    Recomendar usuarios según las ofertas del trabajo

    Explicar cómo mejorar el CV.

    Responder dudas laborales usando RAG.

    Acceder a herramientas (DB, búsqueda, etc.) mediante LangGraph.

## FUNCIONALIDADES PRINCIPALES

    Autenticación JWT (registro, login, rutas protegidas).

    CRUD de ofertas de empleo.

    CRUD de candidaturas (aplicar a una oferta).

    Perfil de usuario editable.

    Chat con IA integrado en el frontend.

    RAG con documentos sobre empleo, CV, entrevistas, etc.

    Workflow N8N que se activa cuando un usuario aplica a una oferta.

    Panel simple para ver tus candidaturas.

    Diseño responsive.

## BACKEND (FastAPI + PostgreSQL)
Tecnologías:

    FastAPI

    Pydantic v2

    PostgreSQL

    SQLAlchemy

    LangChain + LangGraph

    ChromaDB

    JWT

    N8N (webhook)

Tablas mínimas:

    usuarios

    ofertas

    candidaturas

Relaciones:

    Una empresa puede crear muchas ofertas.

    Un usuario recibir muchas ofertas.

    Una oferta puede tener muchas candidaturas.

Endpoints mínimos:

    /auth/register

    /auth/login

    /auth/me

    /ofertas (GET, POST, PUT, DELETE)

    /candidaturas (POST, GET)

    /api/chat (POST)

    /api/chat/history/{id} (GET)

    /webhook/n8n (POST)

## Agente IA:

Construido con LangGraph.

Debe tener al menos 2 tools:

    Tool RAG (consulta a ChromaDB)

    Tool DB (buscar ofertas según filtros)

Memoria conversacional persistente.

Cita fuentes cuando usa RAG.

Documentos para RAG (mínimo 5):

    Cómo mejorar tu CV

    Consejos para entrevistas

    Cómo escribir una carta de presentación

    Errores comunes al buscar empleo

    Guía básica de perfiles profesionales

## FRONTEND (React + Vite)
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

    /ofertas

    /ofertas/:id

    /perfil

    /chat

Componentes clave:

    Formulario de login/registro

    Lista de ofertas

    Detalle de oferta

    Formulario para crear oferta

    Chat con IA

    Header con estado de sesión

    Página de perfil

Estados a manejar:

    loading

    error

    empty

    success

## AUTOMATIZACIÓN N8N
Workflow mínimo:

    Trigger: Webhook desde FastAPI cuando un usuario aplica a una oferta.

    IF: Si la oferta pertenece a una empresa concreta o si el usuario cumple ciertos criterios.

    Acción: Enviar email, registrar evento, o guardar log.

    Exportar JSON al repositorio.


## ROADMAP DE DESARROLLO (RESUMIDO)
Día 1: Diseño BD + estructura backend
Día 2: Autenticación + CRUD ofertas
Día 3: CRUD candidaturas + endpoints IA
Día 4: Agente LangGraph + RAG
Día 5: Frontend base + login + ofertas
Día 6: Chat IA + perfil
Día 7: N8N + despliegue
Día 8: Documentación + pruebas + presentación