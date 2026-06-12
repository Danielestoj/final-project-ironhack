# Asistente D&D — Proyecto FullStack (Python + React + PostgreSQL + IA)

## Descripción

Asistente D&D es una plataforma web inteligente para jugadores y directores de juego de Dungeons & Dragons 5ª edición. Combina un gestor de personajes completo, una base de datos de hechizos y objetos, un tracker de combate, y un chatbot con IA que responde preguntas sobre reglas, tira dados y busca información usando **RAG (Retrieval Augmented Generation)** con **pgvector**.

El proyecto incluye:

- API REST con 10+ recursos principales
- Autenticación JWT con roles (user/admin)
- Base de datos PostgreSQL con SQLAlchemy ORM + pgvector
- Generación de fichas de personaje en PDF (FPDF2)
- Chatbot con IA usando LangGraph + Groq (LLaMA 3.3 70B)
- Búsqueda semántica sobre documentos de reglas (FastEmbed + pgvector)
- Tirada de dados y consulta de hechizos/condiciones mediante tool-calling
- Generación aleatoria de personajes y encuentros
- Sistema de combate por turnos
- Diseño responsive (mobile/tablet/desktop)
- Tests unitarios e integración (pytest + vitest)
- Deploy completo (Railway + Vercel)

## Despliegue Online

**Frontend (Vercel)**: https://final-project-ironhack-mu.vercel.app/
**Backend (Railway)**: https://lively-clarity-production-2458.up.railway.app/

## Stack

- **Backend**: Python 3.12+ · FastAPI · SQLAlchemy · PostgreSQL + pgvector · LangGraph · Groq (LLaMA 3.3 70B) · FastEmbed · FPDF2 · Pydantic · LangChain · pytest
- **Frontend**: React 19 · Vite · React Router v7 · Axios · CSS vanilla responsive · Vitest
- **IA/RAG**: Groq API · FastEmbed (all-MiniLM-L6-v2) · pgvector (cosine similarity) · LangGraph agent con tool-calling

## Funcionalidades principales

### Gestión de personajes
- Crear, editar y eliminar personajes con estadísticas completas (fuerza, destreza, constitución, inteligencia, sabiduría, carisma)
- Gestión de puntos de golpe, dados de golpe, CA, iniciativa, velocidad
- Ataques, equipo, rasgos y habilidades
- Seguimiento de salvación contra muerte e inspiración
- Gestión de niveles y clases
- Exportar ficha de personaje a PDF con diseño profesional
- Vista de ficha completa a página completa

### Hechizos y objetos
- Base de datos completa de hechizos desde el SRD 5.1
- Base de datos de objetos y equipo
- Búsqueda avanzada con filtros por clase, escuela, nivel, tipo
- Búsqueda por texto (ILIKE) en nombre y descripción

### Combate
- Sistema de combate por turnos
- Gestión de iniciativa
- Seguimiento de puntos de golpe y estado
- Daño y curación

### Chatbot con IA (asistente de reglas)
- Responde preguntas sobre reglas de D&D usando RAG
- Tira dados con notación estándar (1d20, 2d6, 1d20+5)
- Busca información de hechizos y condiciones
- Citación de fuentes desde los documentos de reglas
- El asistente decide cuándo usar herramientas (tool-calling autónomo)

### Otras funcionalidades
- Generador aleatorio de personajes completos
- Generador de encuentros
- Gestión de enemigos y monstruos
- Métricas de uso del sistema
- Integración con N8N mediante webhook
- Dashboard de administración

## Estructura del proyecto

```
Final-Proyect/
│
├── backend/                        # API REST (Python FastAPI)
│   ├── main.py                     # Punto de entrada, routers, CORS, excepciones
│   ├── config.py                   # Configuración vía variables de entorno
│   ├── database.py                 # Conexión PostgreSQL + pgvector
│   ├── agente.py                   # Agente LangGraph con tool-calling + RAG
│   ├── ingestar.py                 # Ingesta de documentos → pgvector
│   ├── seed_db.py                  # Seed de hechizos y objetos desde JSON
│   ├── requirements.txt
│   ├── Procfile                    # Railway: comando de inicio
│   ├── railway.json                # Config Railway
│   ├── .railwayignore
│   │
│   ├── models/
│   │   ├── personaje.py            # Modelo de personaje
│   │   ├── usuario.py              # Modelo de usuario + autenticación
│   │   ├── hechizo.py              # HechizoDB
│   │   ├── objeto.py               # ObjetoDB
│   │   ├── combate.py              # Modelo de combate por turnos
│   │   └── documento.py            # DocumentoChunk (pgvector)
│   │
│   ├── routers/
│   │   ├── auth.py                 # Login, registro, perfil
│   │   ├── personajes.py           # CRUD personajes + PDF export
│   │   ├── hechizos.py             # Consulta de hechizos
│   │   ├── objetos.py              # Consulta de objetos
│   │   ├── ia.py                   # Chat IA endpoints
│   │   ├── combate.py              # Sistema de combate
│   │   ├── encuentros.py           # Generador de encuentros
│   │   ├── enemigos.py             # Gestión de enemigos
│   │   ├── clases.py / razas.py    # Catálogos
│   │   ├── condiciones.py          # Condiciones de D&D
│   │   ├── games.py                # Gestión de campañas
│   │   ├── pdf.py / sync.py        # Procesado de PDFs
│   │   ├── metrics.py              # Métricas de uso
│   │   └── cleanup.py              # Limpieza de datos
│   │
│   ├── auth/
│   │   └── jwt.py                  # JWT utils
│   │
│   ├── services/
│   │   └── metrics_service.py      # Servicio de métricas
│   │
│   ├── data/
│   │   ├── hechizos.json           # Datos de hechizos SRD 5.1
│   │   ├── objetos_equipo.json     # Datos de objetos
│   │   └── reglas_basicas.json     # Reglas básicas
│   │
│   ├── docs/                       # Documentos para RAG
│   │   ├── reglas_basicas.txt
│   │   └── trasfondo_y_escenarios.txt
│   │
│   ├── scripts/                    # Utilidades
│   │   ├── extract_srd.py
│   │   ├── pdf_processor.py
│   │   └── sync_to_db.py
│   │
│   ├── games/                      # Documentos por campaña
│   │
│   └── tests/
│       └── test_api.py             # 13 tests de integración
│
├── frontend/                       # Cliente React
│   ├── index.html
│   ├── vite.config.js
│   ├── vercel.json                 # SPA routing para Vercel
│   ├── .env.example
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                 # Router principal
│       ├── index.css               # Estilos globales responsive
│       │
│       ├── api/
│       │   └── client.js           # Axios client con JWT
│       │
│       ├── context/
│       │   └── AuthContext.jsx      # Contexto de autenticación
│       │
│       ├── components/
│       │   ├── Header.jsx          # Navegación principal
│       │   ├── Chat.jsx            # Componente de chat con IA
│       │   ├── CharacterCard.jsx   # Tarjeta de personaje
│       │   ├── CharacterForm.jsx   # Formulario de personaje
│       │   ├── StatBlock.jsx       # Bloque de estadísticas
│       │   ├── PersonajeModal.jsx  # Modal de personaje
│       │   └── ProtectedRoute.jsx  # Ruta protegida
│       │
│       ├── pages/
│       │   ├── HomePage.jsx
│       │   ├── LoginPage.jsx
│       │   ├── RegisterPage.jsx
│       │   ├── PersonajesPage.jsx  # Lista de personajes
│       │   ├── FichaPersonajePage.jsx  # Ficha completa
│       │   ├── HechizosPage.jsx    # Búsqueda de hechizos
│       │   ├── ObjetosPage.jsx     # Búsqueda de objetos
│       │   ├── ChatPage.jsx        # Chat con IA
│       │   ├── AdminPage.jsx
│       │   └── EncuentrosPage.jsx
│       │
│       └── __tests__/
│           └── components.test.jsx # 5 tests de componentes
│
└── README.md                       # Este archivo
```

## Puesta en marcha

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Edita .env con:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/rol_app
#   LLM_API_KEY=gsk_tu-key-de-groq
python -m pytest tests/ -v   # Verificar que funciona
uvicorn main:app --reload    # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edita .env: VITE_API_URL=http://localhost:8000
npm run dev                   # http://localhost:5173
npm run build                 # Build producción
```

## Usuarios de prueba

| Email | Contraseña | Rol |
|---|---|---|
| admin@admin.com | 12345678 | admin |

Los nuevos registros obtienen rol "user".

## Rutas principales

### Frontend
| Ruta | Página |
|---|---|
| `/` | Home |
| `/login` | Login |
| `/register` | Registro |
| `/games/:slug/personajes` | Lista de personajes |
| `/games/:slug/personajes/:id` | Ficha completa de personaje |
| `/games/:slug/hechizos` | Búsqueda de hechizos |
| `/games/:slug/objetos` | Búsqueda de objetos |
| `/games/:slug/chat` | Chat con IA |
| `/games/:slug/encuentros` | Generador de encuentros |
| `/admin` | Panel de administración |

### API (Backend)
| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/auth/registro` | Registro de usuario | — |
| POST | `/auth/login` | Inicio de sesión | — |
| GET | `/auth/perfil` | Perfil del usuario | ✓ |
| GET | `/personajes` | Lista de personajes | ✓ |
| POST | `/personajes` | Crear personaje | ✓ |
| PUT | `/personajes/:id` | Actualizar personaje | ✓ |
| DELETE | `/personajes/:id` | Eliminar personaje | ✓ |
| GET | `/personajes/:id/pdf` | Exportar PDF de ficha | ✓ |
| GET | `/hechizos` | Buscar hechizos (filtros: q, nivel, escuela, clase) | ✓ |
| GET | `/objetos` | Buscar objetos (filtros: q, seccion) | ✓ |
| POST | `/api/chat` | Chat con IA (LangGraph agent) | ✓ |
| POST | `/api/chat/simple` | Chat con IA (fallback RAG) | ✓ |
| POST | `/combate/crear` | Crear combate | ✓ |
| POST | `/combate/:id/next-turn` | Siguiente turno | ✓ |
| POST | `/combate/:id/damage` | Aplicar daño | ✓ |
| GET | `/encuentros/generar` | Generar encuentro aleatorio | ✓ |
| GET | `/clases` | Lista de clases | — |
| GET | `/razas` | Lista de razas | — |
| GET | `/condiciones` | Lista de condiciones | — |
| GET | `/enemigos` | Lista de enemigos | ✓ |
| GET | `/api/metrics/dashboard` | Dashboard de métricas | ✓ |
| GET | `/health` | Health check | — |

## Chatbot con IA (sistema RAG + tools)

El asistente utiliza un agente **LangGraph** con las siguientes capacidades:

1. **RAG (Retrieval Augmented Generation)**:
   - Los documentos de reglas se dividen en chunks de ~500 caracteres
   - Se genera un embedding de 384 dimensiones con FastEmbed (all-MiniLM-L6-v2)
   - Los embeddings se almacenan en PostgreSQL con la extensión pgvector
   - Al recibir una pregunta, se busca por similitud coseno (`<=>`)
   - El contexto recuperado se inyecta en el prompt del sistema

2. **Tool-calling**:
   - El LLM (Groq LLaMA 3.3 70B) recibe definiciones de herramientas
   - Decide autónomamente cuándo llamar a cada herramienta
   - **`tirar_dado(formula)`**: Tira dados con notación D&D (1d20, 2d6, 1d20+5)
   - **`buscar_hechizo(nombre)`**: Busca información de un hechizo por nombre
   - **`buscar_condicion(nombre)`**: Busca información de una condición

3. **Flujo del agente**:
   ```
   Mensaje del usuario
        │
        ▼
   nodo_llm (Groq API + tools definitions)
        │
        ├── ¿tool_calls? ──► nodo_tools (ejecuta función Python)
        │                            │
        │                            └──► nodo_llm (vuelve con resultado)
        │
        └── texto plano ──► Respuesta al usuario
   ```

4. **Modelo**: `llama-3.3-70b-versatile` (Groq, free tier: 30 req/min)

## Tests

```bash
# Backend (pytest)
cd backend
python -m pytest tests/ -v    # 13 tests de integración

# Frontend (vitest)
cd frontend
npx vitest run                 # 5 tests de componentes
```

## Endpoints destacados de la API

### Chat
```json
POST /api/chat
{
  "session_id": "sesion-123",
  "message": "¿qué es cegado?",
  "game_slug": "dnd"
}
→ {
  "response": "**Cegado**: No puedes ver...",
  "session_id": "sesion-123"
}
```

### Hechizos con filtros
```json
GET /hechizos?q=fuego&nivel=3&clase=Mago&escuela=Evocación
→ [
  {
    "nombre": "Bola de fuego",
    "nivel": 3,
    "escuela": "Evocación",
    "descripcion": "..."
  }
]
```

### PDF de personaje
```json
GET /personajes/1/pdf
→ (binario PDF: ficha profesional con bordered cells, checkboxes, stat blocks)
```

## Variables de entorno

### Backend (`.env`)
```
DATABASE_URL=postgresql://user:pass@host:5432/rol_app
SECRET_KEY=clave-segura-64-chars-minimo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:5173,https://tu-app.vercel.app
DEBUG=false
LLM_MODEL=llama-3.3-70b-versatile
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_tu-api-key-de-groq
```

### Frontend (`.env`)
```
VITE_API_URL=http://localhost:8000
```

## Base de datos (PostgreSQL + pgvector)

### Extensiones
- `vector` — pgvector para embeddings (384 dimensiones)

### Tablas principales
- `usuarios` — Usuarios y autenticación
- `personajes` — Personajes de D&D
- `hechizos` — Catálogo de hechizos
- `objetos` — Catálogo de objetos
- `combates` — Sesiones de combate
- `document_chunks` — Chunks de documentos con embeddings vectoriales

### Diagrama ER

```mermaid
erDiagram
    Usuario ||--o{ Personaje : crea
    Usuario ||--o{ Combate : dirige

    Personaje {
        int id PK
        string nombre
        string raza
        string clase
        int nivel
        int fuerza
        int destreza
        int constitucion
        int inteligencia
        int sabiduria
        int carisma
        int pg_maximos
        int pg_actuales
        int ca
        int iniciativa
        int velocidad
        jsonb ataques
        jsonb equipo
        jsonb rasgos
        jsonb habilidades
        boolean inspiracion
        int exitos_muerte
        int fallos_muerte
        jsonb conjuros
    }

    Hechizo {
        int id PK
        string nombre
        int nivel
        string escuela
        string tiempo_conjuro
        string alcance
        string componentes
        string duracion
        string descripcion
        string clase
    }

    Objeto {
        int id PK
        string nombre
        string seccion
        jsonb datos
    }

    Combate ||--o{ Participante : incluye
    Participante {
        int id PK
        string nombre
        int iniciativa
        int pg
        int pg_maximos
        string tipo
    }

    DocumentChunk {
        int id PK
        string chunk_id
        string game_slug
        string filename
        text content
        vector(384) embedding
    }
```

## Matriz de roles y permisos

| Rol | Crear personaje | Editar personaje | Ver chat IA | Admin | Exportar PDF |
|---|---|---|---|---|---|
| admin | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |
| user | ✔️ | ✔️ | ✔️ | ❌ | ✔️ |
