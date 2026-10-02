# ⚙️ Guía de Configuración del Perfil

Este directorio contiene la fuente de datos única (`profile.config.json`) y el esquema JSON (`schema.json`) que gobiernan todos los componentes del perfil de GitHub de **JharlyOk**.

---

## 📂 Archivos en este directorio

| Archivo | Propósito |
| :--- | :--- |
| **`profile.config.json`** | Archivo principal de datos, configuración y toggles de módulos. |
| **`schema.json`** | JSON Schema oficial (Draft 7). Otorga autocompletado y validación en Cursor, VS Code y otros editores. |

---

## 🎛️ 1. Activar / Desactivar Componentes (`modules`)

Puedes encender o apagar cualquier ventana o módulo de tu perfil con un solo booleano (`true`/`false`):

```json
"modules": {
  "header":   { "enabled": true },   // Barra de bienvenida typewriter + 4 Highlight cards
  "banner":   { "enabled": true },   // Editor Neovim con código TypeScript
  "projects": { "enabled": true },   // Árbol de terminal con proyectos destacados
  "stack":    { "enabled": true },   // Matriz de terminal con categorías de tecnologías
  "connect":  { "enabled": true },   // Tarjeta de terminal con canales de contacto y SLAs
  "badges":   { "enabled": true }    // Badges vectoriales clicables (Split-Pill)
}
```

> Al ejecutar `python scripts/build.py`, los módulos desactivados se omiten automáticamente tanto en la generación de assets como en el [README.md](../README.md).

---

## 👤 2. Identidad y Mensajes del Header (`identity`)

```json
"identity": {
  "handle": "JharlyOk",
  "role": "AI-Assisted Systems Builder & Bot Architect",
  "tagline": "Transforming complex distributed ideas into production software through AI acceleration",

  "highlights": [
    { "icon": "bot", "label": "13+ Production Bots", "detail": "Telegram & Discord fleet" },
    { "icon": "audio", "label": "Real-Time Audio", "detail": "Lavalink v4 + LavaSrc pipeline" },
    { "icon": "ai", "label": "Multi-LLM Development", "detail": "Gemini, Claude, Cursor, LLM Arena" },
    { "icon": "infra", "label": "Self-Hosted Infra", "detail": "Docker + Linux VPS + Pterodactyl" }
  ],

  "welcome_messages": [
    "Hey, welcome to my workspace",
    "Building autonomous bot ecosystems",
    "13+ production bots running 24/7",
    "AI-accelerated dev with Gemini & Claude",
    "Real-time audio routing with Lavalink v4"
  ]
}
```

* **`welcome_messages`**: Lista de textos que la animación SMIL Typewriter escribe, pausa y borra cíclicamente.
* **`highlights`**: Las 4 tarjetas horizontales en el Header. Iconos admitidos: `"bot"`, `"audio"`, `"ai"`, `"infra"`, `"web"`.

---

## 🎨 3. Temas (`themes`)

```json
"themes": {
  "dark": "github-dark",
  "light": "github-light"
}
```
Apunta a los archivos en `themes/<nombre>.json`. Si creas un nuevo tema (ej. `dracula.json`), simplemente colócalo aquí.

---

## 💻 4. Editor de Código Neovim (`banner`)

Permite personalizar el archivo simulado en el editor:
* **`filename`**: Nombre de la pestaña activa (ej. `JharlyOk.config.ts`).
* **`filepath`**: Ruta relativa (ej. `src/core/`).
* **`language`**: Etiqueta del badge (ej. `TypeScript`, `Python`, `Rust`).
* **`git_branch`**: Rama mostrada en el statusline inferior (ej. `main`).
* **`code_lines`**: Array de líneas tokenizadas con tipos de sintaxis (`keyword`, `string`, `comment`, `type`, `property`, `function`, `punctuation`).

---

## 🚀 5. Proyectos (`projects`)

```json
"projects": [
  {
    "name": "epic-ai-agents",
    "type": "AI Context Framework",
    "description": "System prompt architecture for LLM-assisted bot development",
    "tags": ["Two-Phase Init", "Zero-Trust", "Repository Pattern"]
  }
]
```

---

## 🛠️ 6. Matriz de Stack (`stack`)

Agrega o reorganiza columnas en el grid de la terminal:
```json
"stack": {
  "ai_toolchain": {
    "label": "AI & LLM Toolkit",
    "items": ["Google Gemini", "Claude", "Cursor", "LLM Arena", "epic-ai-agents"]
  }
}
```

---

## 🌐 7. Canales y Redes (`socials`)

Controla tanto la **Connect Terminal Card** como los **Badges Split-Pill**:
```json
{
  "id": "telegram",
  "label": "Telegram",
  "handle": "@JharlyOk",
  "url": "https://t.me/JharlyOk",
  "accent": "primary",
  "tag": "DIRECT CHAT",
  "description": "Direct message, bot deployments & custom inquiries",
  "latency": "< 1h avg response"
}
```

* **`id`**: Determina el icono SVG vectorial (`telegram`, `discord`, `email`, `github`, `linkedin`, `x`, `web`).
* **`accent`**: Color de acento del badge (`primary`, `secondary`, `success`, `warning`, `danger`).
* **`tag`**: Píldora de categoría en la Connect Card.
* **`latency`**: Indicador SLA de tiempo de respuesta.

---

## ⚡ Comandos Útiles

```bash
# Compilar todos los assets y sincronizar README.md
python scripts/build.py

# Compilar sin modificar README.md
python scripts/build.py --no-readme

# Compilar únicamente un módulo específico (ej. header o connect)
python scripts/build.py --only header
python scripts/build.py --only connect

# Listar todos los builders registrados
python scripts/build.py --list
```
