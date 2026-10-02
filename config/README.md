# ⚙️ Guía de Configuración del Perfil (YAML)

Este directorio contiene la fuente de datos única (`profile.config.yaml`) y el esquema de validación (`schema.json`) que gobiernan todos los componentes del perfil de GitHub de **JharlyOk**.

---

## 📂 Archivos en este directorio

| Archivo | Propósito | ¿Debes editarlo? |
| :--- | :--- | :--- |
| **`profile.config.yaml`** | **Fuente única de la verdad.** Contiene tus datos, proyectos, stack, redes y configuraciones autocontenidas. | **SÍ, es el único archivo a editar.** |
| **`schema.json`** | Esquema JSON Schema (Draft 7). Otorga autocompletado y validación de sintaxis en tiempo real en tu editor (VS Code / Antigravity). | **NO**, es una herramienta técnica del IDE. |

> 💡 **Nota sobre la telemetría**: La caché de métricas de GitHub (`telemetry.json`) se guarda automáticamente en `.cache/` en la raíz del proyecto para mantener este directorio limpio.

---

## 🎛️ 1. Activar / Desactivar Componentes (Control Descentralizado)

Cada sección en `profile.config.yaml` es **completamente autocontenida** y cuenta con sus propios interruptores directos:

| Sección en YAML | Interruptor | ¿Qué activa o desactiva? |
| :--- | :--- | :--- |
| **`identity`** | `enabled: true/false` | Cabecera animada typewriter con tarjetas de sistemas activos. |
| | `telemetry.enabled: true/false` | 3ra fila opcional de mini-pills de telemetría dentro del Header SVG. |
| **`stats`** | `enabled: true/false` | 🖥️ Dashboard terminal grande (880px) de estadísticas de GitHub. |
| | `badges: true/false` | 🔘 Botones split-pill de métricas (`followers`, `repos`, etc.) al pie. |
| **`banner`** | `enabled: true/false` | Editor Neovim con tu configuración TypeScript y resaltado de sintaxis. |
| **`projects`** | `enabled: true/false` | Árbol de terminal con tus sistemas y repositorios destacados. |
| **`stack`** | `enabled: true/false` | Cuadrícula terminal categorizada con tus tecnologías y herramientas. |
| **`socials`** | `banner: true/false` | 🖥️ Banner terminal gigante (880px) `socials --endpoints`. |
| | `badges: true/false` | 🔘 Botones interactivos split-pill de redes sociales. |
| | `links[].enabled: true/false` | Control individual para cada red social (Telegram, Discord, etc.). |

---

## 👤 2. Estructura de las Secciones

### 2.1 Identidad y Bienvenida (`identity`)
```yaml
identity:
  enabled: true       # Muestra u oculta la cabecera completa
  handle: "JharlyOk"
  role: "AI-Assisted Systems Builder & Bot Architect"
  tagline: "Transforming complex distributed ideas into production software"

  highlights:
    - icon: bot
      label: "13+ Production Bots"
      detail: "Telegram & Discord fleet"

  welcome_messages:
    - "Hey, welcome to my workspace"
    - "Building autonomous bot ecosystems"

  telemetry:
    enabled: false    # Mini-pills dentro del Header SVG
```

### 2.2 Estadísticas y Telemetría (`stats`)
Al igual que `socials`, la sección `stats` cuenta con configuración granular avanzada. Puedes personalizar o sobreescribir cada tarjeta del dashboard terminal:
```yaml
stats:
  enabled: true       # Dashboard terminal grande (880px)
  badges: false       # Badges individuales de métricas al pie (split-pill)
  command: "gh telemetry --overview"
  badge_text: "LIVE TELEMETRY"
  badge_accent: "success"  # success, primary, secondary, warning, danger o hex (#...)
  metrics:
    repos:
      enabled: true                     # Mostrar u ocultar la tarjeta
      label: "PUBLIC REPOS"             # Título de la tarjeta
      icon: "repo"                      # Icono vectorial (repo, star, followers, eye, etc.)
      accent: "success"                 # Color de acento
      prefix: ""                        # Prefijo antes del número (ej. "> ")
      suffix: "Active"                  # Sufijo descriptivo
      sub: "open source systems"        # Subtexto descriptivo
      # value: "10+"                    # (Opcional) Valor manual fijo en vez de la API
    stars:
      enabled: true
      label: "TOTAL STARS"
      icon: "star"
      accent: "warning"
      prefix: "★ "
      suffix: "Earned"
      sub: "community stargazers"
    followers:
      enabled: true
      label: "DEV NETWORK"
      icon: "followers"
      accent: "secondary"
      prefix: ""
      suffix: "Followers"
      sub: "{following} following developers"
    views:
      enabled: true
      label: "PROFILE VIEWS"
      icon: "eye"
      accent: "primary"
      prefix: ""
      suffix: "Hits"
      sub: "live hit counter"
```
> [!TIP]
> Si desactivas cualquier tarjeta con `enabled: false`, las tarjetas restantes redistribuyen su ancho simétricamente de forma automática en el grid de 880px. También puedes agregar métricas personalizadas (ej. `uptime`, `commits`, etc.) con su propio `value` y `sub`.

### 2.3 Editor Neovim (`banner`)
```yaml
banner:
  enabled: true       # Editor de código Neovim
  filename: "JharlyOk.config.ts"
  code_lines: [...]
```

### 2.4 Proyectos Destacados (`projects`)
```yaml
projects:
  enabled: true       # Árbol de proyectos
  items:
    - name: "epic-ai-agents"
      type: "AI Context Framework"
      description: "..."
      tags: ["Two-Phase Init", "Zero-Trust"]
```

### 2.5 Matriz de Tecnologías (`stack`)
```yaml
stack:
  enabled: true       # Cuadrícula de tecnologías
  ai_toolchain:
    label: "AI & LLM Toolkit"
    items: ["Google Gemini", "Claude", "Cursor"]
```

### 2.6 Redes Sociales y Contacto (`socials`)
```yaml
socials:
  banner: false       # Tarjeta terminal grande (880px)
  badges: true        # Botones interactivos split-pill
  links:
    - id: "telegram"
      enabled: true
      label: "Telegram"
      url: "https://t.me/JharlyOk"
    - id: "discord"
      enabled: true
      label: "Discord"
      url: "https://discord.com"
```

---

## 🚀 Compilar Cambios

Cada vez que edites `profile.config.yaml`, compila tus cambios localmente ejecutando:

```bash
python scripts/build.py
```

O simplemente haz un `git commit` y súbelo con `git push`: **GitHub Actions lo compilará y desplegará automáticamente en tu repositorio**.
