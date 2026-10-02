# 📘 Guía Avanzada de Arquitectura y Configuración del Perfil

Bienvenido a la documentación técnica de personalización del perfil de GitHub de **JharlyOk**. Este repositorio utiliza un motor SVG modular en Python que compila gráficos vectoriales ultra-nítidos adaptables a temas oscuro y claro sin dependencias externas.

---

## 🏗️ Arquitectura del Sistema

```
JharlyOk/
├── .github/workflows/
│   └── build-profile.yml      # CI/CD: Compilación y despliegue automático en GitHub Actions
├── assets/                    # Artefactos SVG compilados para Dark y Light
│   ├── header-dark.svg / header-light.svg
│   ├── banner-dark.svg / banner-light.svg
│   ├── projects-dark.svg / projects-light.svg
│   ├── stack-dark.svg / stack-light.svg
│   ├── connect-dark.svg / connect-light.svg
│   └── badges/                # Badges vectoriales split-pill individuales
│       ├── telegram-dark.svg / telegram-light.svg
│       └── ...
├── config/
│   ├── profile.config.json    # FUENTE ÚNICA DE LA VERDAD
│   ├── schema.json            # JSON Schema (validación y autocompletado en IDEs)
│   └── README.md              # Referencia rápida
├── docs/
│   └── CONFIGURATION.md       # Este documento
├── scripts/
│   ├── build.py               # CLI principal de compilación y orquestación
│   └── engine/                # Motor modular SVG (Arquitectura por capas)
│       ├── core/              # Núcleo del sistema
│       │   ├── config.py      # Validador y cargador de configuración
│       │   ├── theme.py       # Mapeo de tokens de diseño Primer (Dark/Light)
│       │   └── registry.py    # Decorador @register_builder y registro dinámico
│       ├── svg/               # Capa gráfica y vectores
│       │   ├── primitives.py  # Primitivas SVG (rect, text, circle, terminal_header, etc.)
│       │   └── icons/         # Catálogo de íconos vectoriales SVG individuales (24x24)
│       │       ├── __init__.py# Loader dinámico con caché en memoria
│       │       └── *.svg      # Archivos SVG nativos (telegram, discord, repo, star...)
│       ├── markdown/          # Capa de documentación
│       │   └── readme.py      # Ensamblador dinámico de README.md
│       └── builders/          # Constructores visuales de componentes
│           ├── header.py      # Typewriter SMIL + Highlight cards
│           ├── banner.py      # Editor Neovim con resaltado de sintaxis
│           ├── projects.py    # Terminal con árbol de proyectos
│           ├── stack_matrix.py# Terminal con cuadrícula de tecnologías
│           ├── connect.py     # Terminal con endpoints de comunicación
│           └── badges.py      # Constructor de badges split-pill
└── themes/
    ├── github-dark.json       # Tokens de color oficiales de GitHub Dark
    └── github-light.json      # Tokens de color oficiales de GitHub Light
```

---

## 🎛️ Control de Módulos (Feature Toggles)

En `config/profile.config.json`, la sección `modules` permite activar o desactivar componentes de forma atómica:

```json
"modules": {
  "header":   { "enabled": true },
  "banner":   { "enabled": true },
  "projects": { "enabled": true },
  "stack":    { "enabled": true },
  "connect":  { "enabled": true },
  "badges":   { "enabled": true },
  "telemetry":{ "enabled": true }
}
```

### ¿Qué ocurre cuando desactivas un módulo?
1. **Compilación SVG**: El script `python scripts/build.py` detecta el estado `false` y omite la compilación del módulo correspondiente (`[skip] banner (disabled in config.modules)`).
2. **README sincronizado**: Si ejecutas la compilación estándar, `README.md` se actualiza automáticamente eliminando el bloque `<picture>` del componente desactivado.

---

## 🧩 Guía Sección por Sección

### 1. Header (`header.py`)
* **Animación de Bienvenida**:
  * Utiliza SMIL `<animate>` con `<textPath>`. Sin trucos de opacidad ni rectángulos tapadores.
  * Inicia en el segundo `0.0s`.
  * Escribe carácter por carácter de izquierda a derecha, sostiene la lectura 2.2 segundos y retrocede borrando hacia la izquierda.
* **Highlight Cards**:
  * Diseñadas en cuadrícula de 4 tarjetas simétricas.
  * Barras superiores de acento recortadas matemáticamente con `<clipPath>` (`rx=8`) para no salirse de los bordes redondeados.
  * Puntos verdes de telemetría activa en tiempo real.

### 2. Neovim Code Manifest (`banner.py`)
* **Aspecto**: Ventana macOS con pestañas (`JharlyOk.config.ts` y `package.json`), badge de lenguaje, barra de números de línea, código coloreado por tokens y statusline Neovim (`NORMAL main (utf-8) ● LSP READY`).
* **Personalización**:
  * Modifica `banner.code_lines` en `profile.config.json` para agregar tus propias líneas o funciones.

### 3. Terminal de Proyectos (`projects.py`)
* **Aspecto**: Ventana de terminal ejecutando `ls -la ~/projects --format=detailed`.
* **Estructura**:
  * Cada proyecto muestra su nombre, tipo, descripción resumida y badges de tecnologías clave (`Two-Phase Init`, `Redis`, `Lavalink v4`, etc.).

### 4. Matriz de Stack (`stack_matrix.py`)
* **Aspecto**: Cuadrícula de columnas en terminal ejecutando `cat /etc/stack.yaml`.
* **Personalización**:
  * Puedes agregar nuevas categorías en `config.stack`. El motor recalcula la altura dinámicamente y distribuye las columnas de forma equilibrada.

### 5. Connect Card & Badges (`connect.py` y `badges.py`)
* **Connect Card**: Ventana terminal con 6 tarjetas de canales (Telegram, Discord, Email, GitHub, LinkedIn, X), mostrando etiquetas de prioridad, handles y latencias de respuesta.
* **Badges Split-Pill**: Botones vectoriales individuales de 28px de alto para colocar en cualquier parte de tu GitHub.

---

## 🎨 Personalización de Temas y Colores

Los colores de **todos** los componentes se extraen exclusivamente de `themes/github-dark.json` y `themes/github-light.json`.

```json
{
  "name": "github-dark",
  "label": "GitHub Dark",
  "bg": {
    "canvas": "#0d1117",
    "subtle": "#161b22",
    "inset": "#010409",
    "overlay": "#1c2128"
  },
  "border": {
    "default": "#30363d",
    "muted": "#21262d"
  },
  "fg": {
    "default": "#f0f6fc",
    "muted": "#8b949e",
    "subtle": "#6e7681"
  },
  "accent": {
    "primary": "#58a6ff",
    "secondary": "#bc8cff",
    "success": "#3fb950",
    "warning": "#d29922",
    "danger": "#f85149"
  }
}
```

---

### 6. Badges & Telemetría Dinámica (`badges.py` + `telemetry.py`)
* **Badges de Redes**:
  * Botones split-pill individuales (`assets/badges/{id}-dark.svg` y `light.svg`) con 28px de altura y bordes redondeados Primer (`rx=6`).
* **Métricas Dinámicas de GitHub y Visitas**:
  * Consulta en vivo la API de GitHub (`followers`, `repos`, `stars`) y el contador de visitas (`views`).
  * Formatea números de manera inteligente (`k`, `M`, `+`).
  * Creados con clipPath simétrico, íconos Octicons oficiales (followers, repo, star, eye) y contraste exacto según el tema.
  * Incluye un píxel invisible de registro de visitas para garantizar que cada visita continúe incrementando el contador global.
  * **Tolerancia a fallos**: Si estás offline, utiliza `config/telemetry_cache.json` como fallback seguro.

---

## 🔄 Flujo de Trabajo y Automatización (CI/CD)

El repositorio cuenta con una GitHub Action en `.github/workflows/build-profile.yml`:
1. **Disparadores**:
   * **Automático cada 6 horas (`cron: '0 */6 * * *'`)**: Actualiza las métricas dinámicas (seguidores, estrellas, repositorios, visitas) automáticamente sin intervención humana.
   * **Push a `main`**: Al modificar `config/`, `themes/` o `scripts/`.
   * **Manual (`workflow_dispatch`)**: Puedes forzar la recompilación con 1 clic desde la pestaña "Actions" en GitHub.
2. **Seguridad y Rate Limits**:
   * Utiliza `${{ secrets.GITHUB_TOKEN }}` para disponer de 1,000 peticiones/hora en la API de GitHub.
3. **Persistencia**:
   * Commitea y sincroniza automáticamente `assets/`, `README.md` y `config/telemetry_cache.json` con etiqueta `[skip ci]`.
