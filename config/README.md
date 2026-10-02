# ⚙️ Guía de Configuración del Perfil (YAML)

Este directorio contiene la fuente de datos única (`profile.config.yaml`) y el esquema de validación (`schema.json`) que gobiernan todos los componentes del perfil de GitHub de **JharlyOk**.

---

## 📂 Archivos en este directorio

| Archivo | Propósito | ¿Debes editarlo? |
| :--- | :--- | :--- |
| **`profile.config.yaml`** | **Fuente única de la verdad.** Contiene tus datos, proyectos, stack, redes y feature toggles con comentarios en español. | **SÍ, es el único archivo a editar.** |
| **`schema.json`** | Esquema JSON Schema (Draft 7). Otorga autocompletado y validación de sintaxis en tiempo real en tu editor (VS Code / Antigravity). | **NO**, es una herramienta técnica del IDE. |

> 💡 **Nota sobre la caché**: La telemetría dinámica del sistema (`telemetry.json`) se guarda automáticamente en la carpeta `.cache/` en la raíz del proyecto para mantener este directorio limpio y libre de archivos generados por máquinas.

---

## 🎛️ 1. Activar / Desactivar Componentes (`modules`)

Puedes encender o apagar cualquier ventana o módulo de tu perfil con un simple booleano (`true`/`false`):

```yaml
modules:
  header: true       # Barra de bienvenida typewriter + 4 Highlight cards
  banner: true       # Editor Neovim con código TypeScript
  projects: true     # Árbol de terminal con proyectos destacados
  stack: true        # Matriz de terminal con categorías de tecnologías
  stats: true        # Dashboard banner unificado de telemetría y métricas GitHub (880px)
  connect: false     # Terminal de canales (false recomendado si usas badges en cabecera)
  badges: true       # Botones vectoriales split-pill de redes sociales (100% interactivos)
  telemetry: true    # Badges dinámicos de métricas (followers, repos, stars, visitas)
```

> 💡 **Posición de Badges**: En `profile.config.yaml` puedes configurar `badges.position: "header"` para mostrar tus enlaces de contacto inmediatamente debajo del saludo principal, haciéndolos directamente clickeables sin redundancia.

> Al ejecutar `python scripts/build.py`, los módulos desactivados se omiten automáticamente tanto en la compilación de SVGs como en el [README.md](../README.md).

---

## 👤 2. Identidad y Mensajes del Header (`identity`)

```yaml
identity:
  handle: "JharlyOk"
  role: "AI-Assisted Systems Builder & Bot Architect"
  tagline: "Transforming complex distributed ideas into production software through AI acceleration"

  highlights:
    - icon: bot
      label: "13+ Production Bots"
      detail: "Telegram & Discord fleet"
    - icon: audio
      label: "Real-Time Audio"
      detail: "Lavalink v4 + LavaSrc pipeline"

  welcome_messages:
    - "Hey, welcome to my workspace"
    - "Building autonomous bot ecosystems"
    - "13+ production bots running 24/7"
```

* **`welcome_messages`**: Lista de textos que la animación SMIL Typewriter escribe, pausa y borra cíclicamente.
* **`highlights`**: 4 tarjetas horizontales en cuadrícula con puntos de estado en tiempo real.

---

## 🚀 Compilar Cambios

Cada vez que edites `profile.config.yaml`, compila tus cambios con:

```bash
python scripts/build.py
```

O haz un `git commit` y súbelo con `git push`: **GitHub Actions lo compilará automáticamente en la nube**.
