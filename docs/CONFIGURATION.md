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
│   ├── profile.config.yaml    # FUENTE ÚNICA DE LA VERDAD (100% en YAML con comentarios)
│   ├── schema.json            # JSON Schema (validación y autocompletado en IDEs)
│   └── README.md              # Referencia rápida
├── docs/
│   └── CONFIGURATION.md       # Este documento
├── scripts/
│   ├── build.py               # CLI principal de compilación y orquestación
│   └── engine/                # Motor modular SVG (Arquitectura por capas)
│       ├── core/              # Núcleo del sistema
│       │   ├── config.py      # Validador y cargador de configuración YAML
│       │   ├── theme.py       # Mapeo de tokens de diseño Primer (Dark/Light)
│       │   ├── telemetry.py   # Telemetría en vivo con GitHub API y Komarev
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
│           ├── stats.py       # Dashboard banner de telemetría y stats GitHub (880px)
│           ├── connect.py     # Terminal con endpoints de comunicación
│           └── badges.py      # Constructor de badges split-pill
├── .cache/
│   └── telemetry.json         # Caché local de métricas de GitHub y visitas
└── themes/
    ├── github-dark.json       # Tokens de color oficiales de GitHub Dark
    └── github-light.json      # Tokens de color oficiales de GitHub Light
```

---

## 🎛️ Control de Módulos (Feature Toggles) y Posicionamiento

En `config/profile.config.yaml`, la sección `modules` permite activar o desactivar componentes de forma limpia:

```yaml
modules:
  header: true       # Saludo máquina de escribir + highlight cards
  banner: true       # Editor de código Neovim
  projects: true     # Árbol de proyectos en terminal
  stack: true        # Cuadrícula de tecnologías
  stats: true        # Dashboard banner unificado de telemetría (880px)
  connect: false     # Terminal de canales (false recomendado si usas badges en cabecera)
  badges: true       # Botones split-pill de redes sociales (100% interactivos)
  telemetry: true    # Métricas dinámicas en badges (followers, repos, stars, visitas)
```

### 📍 Ubicación de Badges (`badges.position` y `telemetry.position`)

Puedes posicionar tus badges de contacto en la cabecera para máxima interactividad:

```yaml
badges:
  position: "header"    # "header" (debajo del saludo), "footer" (al final), o "both"

telemetry:
  position: "footer"    # "footer" (al pie) o "header"
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
* **Telemetría Integrada (3ra Fila)**:
  * Permite incorporar métricas dinámicas directamente en el lienzo del Header SVG vía `header.telemetry.enabled: true`.
  * **Control granular individual**: Puedes activar o desactivar cada métrica en `profile.config.yaml`:
    * `followers: true` (seguidores en GitHub)
    * `repos: true` (repositorios públicos)
    * `stars: false` (estrellas ganadas; puedes ocultarlo si tienes 0)
    * `views: true` (contador de visitas en vivo)
  * El motor calcula simétricamente el ancho de las pastillas vectoriales (*pills*) y su espaciado en función de cuántas métricas actives.

### 2. Neovim Code Manifest (`banner.py`)
* **Aspecto**: Ventana macOS con pestañas (`JharlyOk.config.ts` y `package.json`), badge de lenguaje, barra de números de línea, código coloreado por tokens y statusline Neovim (`NORMAL main (utf-8) ● LSP READY`).
* **Personalización**:
  * Modifica `banner.code_lines` en `profile.config.yaml` para agregar tus propias líneas o funciones.

### 3. Terminal de Proyectos (`projects.py`)
* **Aspecto**: Ventana de terminal ejecutando `ls -la ~/projects --format=detailed`.
* **Estructura**:
  * Cada proyecto muestra su nombre, tipo, descripción resumida y badges de tecnologías clave (`Two-Phase Init`, `Redis`, `Lavalink v4`, etc.).

### 4. Matriz de Stack (`stack_matrix.py`)
* **Aspecto**: Cuadrícula de columnas en terminal ejecutando `cat /etc/stack.yaml`.
* **Personalización**:
  * Puedes agregar nuevas categorías en `config.stack`. El motor recalcula la altura dinámicamente y distribuye las columnas de forma equilibrada.

### 5. GitHub Stats & Telemetry Dashboard (`stats.py`)
* **Aspecto**: Banner panorámico de 880px con ventana macOS ejecutando `gh telemetry --overview`.
* **Métricas Principales**: 4 tarjetas de alto impacto con acentos de color Primer:
  * **Public Repos**: Repositorios públicos activos (`3fb950` Success).
  * **Total Stars**: Estrellas acumuladas en proyectos (`d29922` Warning).
  * **Dev Network**: Seguidores y red de desarrolladores (`bc8cff` Purple).
  * **Profile Views**: Contador de visitas en vivo (`58a6ff` Primary Blue).
* **Statusline Inferior**: Línea de estado con antigüedad como desarrollador (Tenure: Since 2020), flota de bots autónomos y pipeline de audio.

### 6. Badges Split-Pill Interactivos (`badges.py`)
* **Aspecto**: Botones vectoriales individuales de 28px de alto con bordes redondeados (`rx=6`).
* **Interacción Real**: Al insertarse en el `README.md` como etiquetas `<a><picture><img></picture></a>`, cada badge es un enlace 100% clickeable individualmente (Telegram, Discord, Email, GitHub, LinkedIn, X).
* **Ubicación Flexible**: Con `badges.position: "header"` en `profile.config.yaml`, los badges se muestran inmediatamente debajo del saludo principal para interacción instantánea de los visitantes.

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

### 7. Badges & Telemetría Dinámica (`badges.py` + `telemetry.py`)
* **Badges de Redes**:
  * Botones split-pill individuales (`assets/badges/{id}-dark.svg` y `light.svg`) con 28px de altura y bordes redondeados Primer (`rx=6`).
* **Métricas Dinámicas de GitHub y Visitas**:
  * Consulta en vivo la API de GitHub (`followers`, `repos`, `stars`) y el contador de visitas (`views`).
  * Formatea números de manera inteligente (`k`, `M`, `+`).
  * Creados con clipPath simétrico, íconos Octicons oficiales (followers, repo, star, eye) y contraste exacto según el tema.
  * Incluye un píxel invisible de registro de visitas para garantizar que cada visita continúe incrementando el contador global.
  * **Tolerancia a fallos**: Si estás offline, utiliza `.cache/telemetry.json` como fallback seguro.

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
   * Commitea y sincroniza automáticamente `assets/`, `README.md` y `.cache/telemetry.json` con etiqueta `[skip ci]`.
