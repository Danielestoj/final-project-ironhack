# AI Log — Asistente D&D

Registro de interacciones con IA durante el desarrollo del proyecto.

---

## 2026-06-03 — Refactor de PDF + migración hechizos/objetos a DB + ficha completa

- **Herramienta**: opencode (DeepSeek)
- **Contexto**: El proyecto tenía hechizos y objetos en archivos JSON planos, la ficha de personaje se mostraba en un modal, y la exportación a PDF era básica.

- **Trabajo realizado**:

  ### PDF export profesional
  - Reescribí `exportar_pdf()` en `routers/personajes.py` para generar una ficha de personaje imprimible en A4 con:
    - Celdas con bordes para todos los campos
    - Checkboxes para booleanos (inspiración, proficiencia, salvaciones contra muerte)
    - Bloques de estadísticas con puntuación + modificador
    - Celdas vacías para escribir a mano
    - Salto de página automático

  ### Hechizos y objetos en base de datos
  - Creé `HechoDB` y `ObjetoDB` como modelos SQLAlchemy
  - Escribí `seed_db.py` que carga `hechizos.json` y `objetos_equipo.json` desde JSON a PostgreSQL
  - Modifiqué `routers/hechizos.py` para consultar desde DB con filtros `clase`, `nombre`, `descripcion` (ILIKE)
  - Modifiqué `routers/objetos.py` para consultar desde DB con filtro `seccion`

  ### Ficha de personaje a página completa
  - Creé `FichaPersonajePage.jsx` en ruta `/games/:slug/personajes/:id` con modo edición/vista completa
  - Simplifiqué `PersonajesPage.jsx` eliminando el modal y usando navegación por ruta
  - Añadí botón de exportar PDF desde la ficha completa

  ### Búsqueda avanzada
  - Añadí filtro de clase (12 clases) en `HechizosPage.jsx`
  - Cambié etiqueta de filtro a "Todos los tipos" en `ObjetosPage.jsx`

  ### Diseño responsive
  - Añadí media queries para 1024px, 780px, 500px
  - Grid adaptable: 3 columnas → 2 columnas → 1 columna
  - Stats compactos en resoluciones medias, apilados en móvil

  ### Quick-update en fichas
  - Inspiración, salvaciones contra muerte y puntos de conjuro clickables sin modo edición
  - Función `quickUpdate()` que guarda directamente al backend

- **Tiempo con IA**: ~4h | **Tiempo sin IA (estimado)**: ~10-12h

---

## 2026-06-10 — Planificación de deploy + migración a pgvector + Groq

- **Herramienta**: opencode (DeepSeek)
- **Contexto**: Se decidió migrar de ChromaDB a pgvector y de LLM local (LM Studio) a Groq para poder hacer deploy en Railway (sin filesystem persistente). Se analizaron opciones de hosting.

- **Decisiones tomadas**:
  - **Hosting**: Backend en Railway, Frontend en Vercel, BD en Railway PostgreSQL
  - **LLM**: Groq (gratuito, `llama-3.3-70b-versatile`, 30 req/min)
  - **Vector DB**: pgvector en lugar de ChromaDB (misma BD PostgreSQL, sin servicio extra)
  - **Embeddings**: FastEmbed (`all-MiniLM-L6-v2`, 384 dimensiones) — Python puro, sin GPU
  - **LangChain + LangGraph**: Se mantienen pero `ChatOpenAI` → `ChatGroq`

- **Problemas identificados**:
  - ChromaDB requiere filesystem persistente → incompatible con Railway
  - LM Studio requiere GPU local → inviable en producción
  - El `.env` local tenía valores de desarrollo que podían filtrarse al deploy

- **Tiempo con IA**: ~2h | **Tiempo sin IA (estimado)**: ~4-5h

---

## 2026-06-11 — Migración ChromaDB → pgvector + refactor agente

- **Herramienta**: opencode (DeepSeek)
- **Contexto**: Ejecución de la migración planificada: reemplazar ChromaDB y ChatOpenAI/ChatGroq por pgvector + FastEmbed + OpenAI-compatible nativo.

- **Trabajo realizado**:

  ### Modelo pgvector
  - Creé `models/documento.py` con `DocumentoChunk(SQLAlchemy)`: `Vector(384)` para embeddings
  - `CREATE EXTENSION IF NOT EXISTS vector` en startup

  ### Rewrite de agente RAG
  - `agente.py`: Reemplacé `ChromaDB` por pgvector (`<=>` cosine distance)
  - Reemplacé `ChatGroq` + `bind_tools()` (daba error con imágenes) por `OpenAI` nativo + tool definitions en formato OpenAI API
  - Misma estructura de grafo LangGraph (llm → tools → llm → END)
  - Conversión manual LangChain messages ↔ OpenAI format

  ### Rewrite de ingesta
  - `ingestar.py`: Reemplacé ChromaDB por FastEmbed + pgvector INSERT

  ### Configuración
  - `config.py`: Ajustado para usar `LLM_BASE_URL` + `LLM_API_KEY` (apunta a Groq)
  - `requirements.txt`: Eliminados `chromadb`, `langchain-groq`, `langgraph-prebuilt`
  - Añadidos `pgvector==0.4.2`, `fastembed==0.8.0`

  ### Deploy config
  - `Procfile`, `railway.json`, `.railwayignore` para Railway
  - `vercel.json` con rewrite SPA para Vercel

- **Problemas durante el desarrollo**:
  - `langchain-groq==2.2.1` no existía en PyPI → corregido a `1.1.3`
  - `langchain-groq==1.1.3` daba error `"Cannot read image.png"` en tool-calling → eliminado completamente, reemplazado por `OpenAI` nativo
  - PostgreSQL local sin extensión vector → tests saltan gracefulmente
  - Railway no inyectaba `DATABASE_URL` → añadido fallback con `PGHOST`/`PGPORT`/etc.

- **Tiempo con IA**: ~6h | **Tiempo sin IA (estimado)**: ~12-15h

---

## 2026-06-11 — Debugging de deploy (Railway + Vercel)

- **Herramienta**: opencode (DeepSeek)
- **Contexto**: Durante el deploy a Railway y Vercel surgieron múltiples problemas de configuración.

- **Problemas y soluciones**:

  ### Railway no encuentra PostgreSQL
  - **Síntoma**: `connection to server at "localhost" port 5432 failed`
  - **Causa**: No se había añadido PostgreSQL como servicio en Railway
  - **Solución**: Añadir PostgreSQL plugin en Railway Dashboard

  ### CORS bloquea peticiones desde Vercel
  - **Síntoma**: `No 'Access-Control-Allow-Origin' header`
  - **Causa**: `ALLOWED_ORIGINS` no configurada
  - **Solución**: Añadir `ALLOWED_ORIGINS=https://final-project-ironhack-mu.vercel.app` en Railway

  ### Error 500 en chat con IA
  - **Síntoma**: `Cannot read "image.png" (model does not support image input)`
  - **Causa**: `langchain-groq==1.1.3` tiene un bug al procesar tool-calling, intenta validar imágenes incluso con texto plano
  - **Solución**: Eliminar `ChatGroq` + `bind_tools()`, usar `OpenAI` nativo con definiciones de herramientas en formato API

  ### Error de conexión a Groq
  - **Síntoma**: Chat no responde, login funciona pero chat no
  - **Causa**: Se usaba una API key de xAI/Grok (`xai-...`) en lugar de Groq (`gsk_...`)
  - **Solución**: Generar API key correcta en https://console.groq.com

  ### `.env` local con valores de desarrollo
  - **Síntoma**: El `.env` contenía `LLM_BASE_URL=http://localhost:1234/v1` y `LLM_MODEL=qwen2.5-vl-3b-instruct`
  - **Riesgo**: Si Railway copia el `.env`, sobreescribe las variables de entorno y apunta a localhost
  - **Solución**: Añadir `.env` a `.gitignore` y crear `.railwayignore` para excluirlo del build

- **Tiempo con IA**: ~3h | **Tiempo sin IA (estimado)**: ~6-8h

---

## Resumen de uso de IA

| Fecha | Área | Herramienta | Tiempo IA | Tiempo estimado sin IA |
|---|---|---|---|---|
| 03/06/2026 | PDF, DB, UI, responsive | opencode | ~4h | ~10-12h |
| 10/06/2026 | Planificación deploy, arquitectura | opencode | ~2h | ~4-5h |
| 11/06/2026 | Migración pgvector, refactor agente | opencode | ~6h | ~12-15h |
| 11/06/2026 | Debugging deploy | opencode | ~3h | ~6-8h |
| **Total** | | | **~15h** | **~32-40h** |
