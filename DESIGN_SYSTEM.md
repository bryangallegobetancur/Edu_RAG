# Design System — Asistente RAG · Proceso Administrativo

> **Fuente de verdad** para el diseño y desarrollo de la interfaz web de la aplicación.
> Cualquier desarrollador o IA debe leer este documento antes de crear o modificar UI.

**Estado del documento:** describe el estado **actual** del proyecto (`web/`), que implementa ciertas partes; el resto se marca como **Recomendado**. No describe componentes inexistentes como si existieran (ver §5).

---

## 1. Design System Overview

### Propósito

Unificar el lenguaje visual, el comportamiento, la accesibilidad y la experiencia de usuario de la aplicación **Asistente RAG del Proceso Administrativo**, de modo que cualquier persona o IA pueda construir nuevas pantallas y componentes sin adivinar reglas de diseño.

### Alcance
- **Dentro de alcance:** la capa web `web/` (React 18 + Vite). Tokens de diseño, componentes, layout, estados, responsive, dark mode, accesibilidad.
- **Fuera de alcance:** backend (FastAPI), pipeline RAG (LangChain/ChromaDB), CLI, evaluación (LangSmith).

### Principios de diseño
1. **Consistencia sobre cantidad.** Un solo patrón por tipo de interacción.
2. **Claridad sobre decoración.** La interfaz está al servicio del contenido conversacional (chat RAG) y la información de fuentes.
3. **Fuentes visibles (citations).** Cada respuesta del asistente cita sus fuentes (archivo + página); la UI debe mostrarlas sin distraer.
4. **Estados siempre explícitos.** Carga, error, vacío y éxito siempre comunicados.
5. **Accesible por defecto (WCAG 2.2 AA).**
6. **Responsive con degradación elegante.**

### Filosofía visual
- Estética **minimalista y funcional**: fondos suaves, un único color de acento, burbujas de mensaje, radios redondeados moderados (8 px / 14 px), sombras sutiles de baja elevación.
- Sin imágenes decorativas ni librería de iconos: se usan **emojis inline** como pictogramas.
- Dos temas: **light** y **dark**, activados por el atributo `data-theme` en `<html>`.

### Principios UX
- **Una pantalla, una tarea:** el chat es la pantalla principal; cada pantalla externa resolverá una sola tarea.
- **Feedback inmediato:** submit visible (typing indicator, cursor de streaming), stop de generación, confirmación de feedback de respuesta.
- **Nada inventado:** el asistente responde solo con contenido indexado; si no hay datos lo indica explícitamente.
- **Reducción de carga cognitiva:** las fuentes se muestran colapsadas por defecto (acordeón) y se expanden solo cuando el usuario lo pide.

### Reglas generales obligatorias
1. Usar **únicamente design tokens** para color, tipografía y radius. No valores sueltos.
2. No agregar colores nuevos sin justificación y sin registrar su token.
3. Todo componente interactivo debe tener estado de **focus visible** y ser operable por teclado.
4. Toda acción destructiva (ej. "Nueva conversación") debe ser revisable antes de ejecutarse.
5. Todo texto debe estar en **español** (`lang="es"`).
6. Las interacciones nuevas deben regirse por el **patrón de componentes existentes**.

---

## 2. Design Tokens

Los tokens viven en `web/src/styles/index.css`. Actualmente solo están centralizados los colores, la tipografía de sistema, los radios y la transición; spacing y elevaciones son valores fijos. **Los tokens que aún no existen están marcados como [Recomendado].**

### 2.1 Colors

El sistema de color se define bajo `:root` (base) y las reglas `[data-theme="light"]` / `[data-theme="dark"]`.

#### Light

| Token | Valor | Uso | Contraste sobre `--bg` |
|---|---|---|---|
| `--bg` | `#f4f6fb` | Fondo general de la app | s/n |
| `--bg-elev` | `#ffffff` | Superficies elevadas (header, footer, burbujas, tarjetas) | alto |
| `--bg-soft` | `#eef2f9` | Superficies suaves (botones, inputs, chips) | alto |
| `--text` | `#1a2235` | Texto principal | > 10:1 ✅ AA |
| `--text-soft` | `#5b677d` | Texto secundario (descripciones, cuerpo de fuentes) | ~5.0:1 ✅ AA |
| `--text-muted` | `#8a93a6` | Metadatos, captions, hints (11–12 px) | ~2.8:1 ⚠️ **por debajo de 4.5:1** |
| `--border` | `#e3e8f1` | Líneas divisorias, bordes de campos | — |
| `--accent` | `#2563eb` | Acción primaria, enlaces, foco, cursor | ~7.0:1 ✅ AA |
| `--accent-soft` | `#dbeafe` | Hover / fondo suave del acento | — |
| `--accent-contrast` | `#ffffff` | Texto sobre `--accent` | ~7.0:1 ✅ AA |
| `--user-bubble` | `#2563eb` | Burbuja del usuario | — |
| `--user-text` | `#ffffff` | Texto en burbuja de usuario | — |
| `--assistant-bubble` | `#ffffff` | Burbuja del asistente | — |
| `--source-bg` | `#f8fafc` | Fondo de tarjetas de fuente | — |
| `--source-hover` | `#eef2f9` | Hover de tarjetas de fuente | — |
| `--ok` | `#16a34a` | Feedback de éxito | — |
| `--error` | `#dc2626` | Errores, acción stop, valoración negativa | — |
| `--info` | `#2563eb` | Feedback informativo | — |

> ⚠️ **Inconsistencia documentada:** `--text-muted` (light) no cumple 4.5:1 sobre `--bg`/`--bg-elev`. Es texto pequeño (11–12 px: hints, captions, metadatos). **Solución recomendada:** oscurecer a `#6b7286`. El contraste de `--border` es deliberadamente bajo (no es texto).

**Recomendado.** Tokens adicionales que no existen hoy:
```
--color-muted        (dark: mantener #768390)
--focus-ring         (para estados de foco unificados)
--ok-soft / --error-soft  (fondo de badges de feedback por tema)
```

#### Dark

Los valores equivalentes están en `[data-theme="dark"]` (ver §16).

### 2.2 Typography

| Token [Recomendado] | Tamaño / peso | Uso actual |
|---|---|---|
| `--font` | `"Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif` | Todo el texto |
| Display / h1 (empty) | 22 px / 700 | Título de empty state |
| Header brand (h1) | 17 px / 700 | Título en header |
| Body text | 15 px / 400 | Burbujas, textarea de input |
| Body meta | 14 px / 400 | Descripciones, sugerencias |
| Small | 13 px / 400 | Tarjetas de fuente, ítems de documentos |
| Caption / meta | 12 px / 400–600 | Subtítulo de marca, titulares de sección, badges |
| Hint / micro | 11 px / 400–600 | Estadísticas de documentos, hint al pie |
| Label (doc-list, sources-title) | 12 px / 600, uppercase, `letter-spacing: .04em` | Títulos de listas |
| Button / link | 13–15 px / 500–700 | Botones |

- Line-height: `1.5` (textarea), `1.55` (fuentes), `1.6` (burbujas y cuerpo), `1` (iconos y barras).
- `letter-spacing`: texto normal `normal`; titulares de listas `.04em`.
- Tipografía únicamente de sistema: sin Google Fonts ni cargas externas.

### 2.3 Spacing — **[Recomendado]**

Actualmente **no hay tokens de spacing**; los valores se escriben inline (gap/padding de 2–24 px). Se recomienda centralizar la escala base de 4 px:

| Token | Valor | Cuándo usarlo |
|---|---|---|
| `space-1` | 4 px | Separaciones mínimas (dots de typing, micro-gaps) |
| `space-2` | 6 px | Gaps compactos entre acciones secundarias |
| `space-3` | 8 px | Entre icono y texto, paddings de chips |
| `space-4` | 10 px | Gaps de agrupación de botones |
| `space-5` | 12 px | Paddings de inputs/cards, gap entre elementos |
| `space-6` | 14 px | Paddings de campos de entrada |
| `space-7` | 16 px | Paddings de botones principales, gaps de secciones |
| `space-8` | 20 px | Paddings de panel (mensajes, footer) |
| `space-9` | 24 px | Paddings de secciones / empty state |
| `space-10` | 32 px | Separación de bloques mayores |

**Regla:** preferir múltiplos de 4. No usar valores sueltos (3, 5, 7, 13 px…).

### 2.4 Border Radius

| Token | Valor | Uso real |
|---|---|---|
| `--radius-sm` | `8 px` | Botones, inputs, tarjetas de fuente, listas de documentos |
| `--radius` | `14 px` | Burbujas de chat, textarea, botón enviar |
| pill | `999 px` | Chips/badges (contador de fragmentos, página de fuente) |
| circle | `50%` | Avatares |

**Recomendado:** tokenizar el pill como `--radius-full: 999px`.

### 2.5 Shadows

| Nivel | Valor (light) | Uso |
|---|---|---|
| `--shadow` (único) | `0 1px 3px rgba(20,30,60,0.06), 0 4px 16px rgba(20,30,60,0.06)` | Burbujas de chat |

El proyecto define **un solo nivel de elevación**. **[Recomendado]** ampliar a `--shadow-sm` (campos), `--shadow-md` (cards/popover), `--shadow-lg` (modales/drawer). Nunca sombras de gran difusión sobre fondos no elevados.

### 2.6 Borders

- Grosor: **1 px** en todos los bordes.
- Estilo: `solid` siempre.
- Color: `--border` (light `#e3e8f1`, dark `#2a313c`) para todos los contornos; `--accent` en hover de botones cuando corresponda.
- Uso: contorno de cards, header, footer, chips, tarjetas de fuente, burbuja del asistente.

### 2.7 Breakpoints

El proyecto define **un solo breakpoint** en `web/src/styles/index.css`:

| Breakpoint | Media query | Propósito |
|---|---|---|
| Mobile | `@media (max-width: 640px)` | Reducir paddings, ocultar `.brand-sub`, burbujas al 88 %, botones compactos |
| Desktop (valor base) | — (más de 640 px) | Layout completo, ancho máximo 980 px |

**[Recomendado]** añadir un breakpoint `>= 1024 px` para pantallas grandes manteniendo el mismo diseño centrado.

---

## 3. Layout System

### Container
`.app` es el contenedor global:
- `display: flex; flex-direction: column; height: 100vh`.
- `max-width: 980px; margin: 0 auto` (columna centrada en desktop).
- En móvil el contenedor ocupa el 100 % del ancho.

### Grid / Columnas
**No existe grid de columnas.** El layout es de **una sola columna** (chat) compuesto verticalmente. **[Recomendado]** si en el futuro hay pantallas tipo dashboard, definir un grid de 12 columnas con gutters de 16 px, manteniendo el chat en una sola columna.

### Secciones verticales del layout actual
| Sección | Selector | Comportamiento |
|---|---|---|
| Header / Navbar | `.app-header` | Fijo al tope, `border-bottom`, fondo `--bg-elev`, padding `14px 20px` (móvil `10px 14px`) |
| Main | `.app-main` | `flex: 1; min-height: 0`, columna |
| Chat view | `.chat-view` | Flex column, `min-height: 0` |
| Messages | `.messages` | Scroll interno, gap 20 px |
| Fuentes | `.sources` (dentro de `.message`) | Colapsadas bajo la burbuja, acordeón |
| Footer compositor | `.chat-footer` | `border-top`, fondo `--bg-elev`, textarea + botón + hint (gap 8 px) |

### Cards
Patrón de "card" informal usado en:
- **Tarjetas de fuente** `.source-card`: fondo `--source-bg`, borde `--border`, radio 8 px; header clickeable + contenido colapsable (acordeón).
- **Lista de documentos** `.doc-list`: título + filas `.doc-item`.

### Page layouts
La app es **single-page** (sin router). No existe layout de página múltiple ni sidebar. Patrón de chat en columna central de 980 px.

---

## 4. Components

> **Estado general:** el proyecto es una webapp de chat. Muchos componentes de formulario complejos (Select, DatePicker, Table…) **no existen** y no deben presentarse como existentes; se marcan **Recomendado** cuando aportan valor futuro.

### Button — primario y secundario

**Purpose** — Disparar una acción.

**Anatomy** — `<button>` + texto.
- Primario `.send-btn`: fondo `--accent`, texto `--accent-contrast`, radio 14 px, peso 600.
- Secundario: `.upload-btn`, `.theme-toggle`, `.clear-btn` (fondo `--bg-soft` o transparente, borde `--border`, radio 8 px).
- Danger: `.send-btn.stop` (fondo `--error`).

**Variantes** — `primario` / `secundario` / `danger` (stop).

**States** — Default; Hover (primario `filter: brightness(1.08)`; secundarios `background: --accent-soft` + borde `--accent`); Focus ❌ (ver accesibilidad); Disabled (`.upload-btn:disabled { opacity: .5; cursor: not-allowed }`, textarea disabled, thumbs disabled, clear deshabilitado durante streaming).

**Behavior** — Submit de formulario o acción puntual; nunca navegación (no hay router).

**Responsive** — En móvil los secundarios bajan a 12 px con padding menor.

**Accessibility** — 🔴 **`:focus-visible` sin definir** para `.send-btn`, `.upload-btn`, `.clear-btn`, `.theme-toggle`, `.thumb-btn` y sugerencias (CSS no lo declara; el `outline` del navegador se pierde con estilos custom). **Recomendado:**
```css
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
```

**Usage** — `<button className="send-btn" type="submit">Enviar ➤</button>`

**Do** — Botones como `<button>` nativo (semántica correcta); foco visible unificado.
**Don't** — No usar `div` clickeables; no colos hardcode que no sean tokens.

### Icon Button

**Purpose** — Acción compacta de solo icono.

**Actual:** `ThemeToggle` (🌙/☀️), `thumb-btn` (👍/👎), botones con emoji en sugerencias y upload. Todos son `<button>` con emoji como contenido.

**Anatomy** — `button` + emoji + `title`/`aria-label` opcional.

**Variantes** — toggle de tema, valoración thumb (up/down/disabled).

**States** — Default; Hover (fondo `--bg-soft` + borde `--accent`); Active (thumb: up = `#dcfce7`/`--ok`; down = `#fee2e2`/`--error`); Disabled.

**Accessibility** — ⚠️ `ThemeToggle` tiene `aria-label` ✓; los thumbs no tienen `aria-label`/`aria-pressed` dinámicos. **[Recomendado]** `aria-label="Valorar respuesta"` + `aria-pressed` en cada thumb.

**Do** — `title` + `aria-label` en todos los icon-only; estado hover; área táctil mínima 40 px.
**Don't** — No usar colores hardcode (ver `#dcfce7`/`#fee2e2` en §16); conservar el estado disabled tras valorar (ya implementado).

### Link

**No existe** ningún `<a>` en la app (single-page, sin router). **[Recomendado]** si se agrega navegación: estilo primario con `--accent`, underline en hover y `:focus-visible` con outline del accent.

### Input / Textarea

Único input real: el `<textarea>` del compositor de chat.

**Purpose** — Capturar el mensaje del usuario con auto-resize (máx. 160 px).

**Anatomy** — `textarea` (rows=1) + botón de enviar (o `Detener` si `isStreaming`).

**States:**
- Default: fondo `--bg-soft`, borde `--border`, radio `--radius`.
- Focus: `border-color: --accent` + `box-shadow: 0 0 0 3px var(--accent-soft)` ✓.
- Placeholder: `--text-muted` (⚠️ contraste).
- Disabled: `opacity: 0.6` durante streaming ✓ (`resize: none`, `max-height: 160px`).

**Behavior** — Enter envía; `Shift+Enter` salto de línea; auto-foco al terminar streaming; auto-resize; `disabled` mientras `isStreaming`.

**Accessibility** — ⚠️ Usa solo `placeholder` sin `aria-label`. **[Recomendado]** añadir `aria-label="Mensaje"` (no depender solo del placeholder).

**Do** — `aria-label`/label, foco con ring, `disabled` durante envío.
**Don't** — No usar el placeholder como única etiqueta; no sin límite de altura (scroll infinito).

### File Upload (PDF)

**Implementado** — `PdfUpload`.

**Purpose** — Subir un PDF del curso para indexación, con progreso.

**Anatomy** — `input type=file` oculto + botón `.upload-btn` + `.progress` (%) + `.upload-status` (ok/info/error).

**States** — Default; Busy (botón disabled + `%`); Success (`.upload-status.ok`); Error (`.upload-status.error`); Info (`.upload-status.info`).

**Behavior** — `input` oculto accionado por el botón; limpia el `value` tras la subida; `onchange` → `uploadPdf` (XMLHttpRequest con progreso).

**Accessibility** — ⚠️ `input` oculto sin label asociada, estado sin `role="status"`. **[Recomendado]** `aria-label` en el botón y `role="status"`/`aria-live="polite"` en el estado.

**Do** — Mostrar siempre el estado de subida (`%`/ok/error).
**Don't** — No permitir múltiples archivos (el backend ingiere uno por request).

### Badge / Chip

**Implementado parcial** — `.doc-item-chunks` (contador) y `.source-page` (p. X).

**Anatomy** — `span`: fondo `--bg-soft`, `color: --text-muted`, radio `999px`, padding `2px 8px`, font-size 11–12 px.

**Variantes** — Dato numérico ("N fragmentos"), referencia de página ("p. X").

**Do** — Solo metadatos no críticos; radio pill; texto ≥ 4.5:1 (⚠️ `--text-muted`).
**Don't** — No usar chips para acciones clickeables.

### Card

**Implementado parcial** — patrón `.source-card` y `.doc-list`.

**Source card** (acordeón): fondo `--source-bg`, borde `--border`, radio 8 px, header clickeable (icono + nombre truncado + página + chevron) y contenido `.source-content` (`pre-wrap`, `max-height: 240px`, `overflow-y: auto`).

**Doc item** (fila): icono, nombre (ellipsis), chip de fragmentos.

**Do** — Ellipsis en títulos largos (`white-space: nowrap; overflow: hidden; text-overflow: ellipsis`); scroll vertical limitado.
**Don't** — No usar texto múltiple sin `min-width`/ellipsis que desborde en móvil.

### Accordion

**Implementado** — las tarjetas de fuente (una a la vez, `openIndex`).

**Behavior** — Un clic abre una tarjeta y cierra la anterior (`setOpenIndex(open ? null : i)`).

**Estados** — Cerrado (chevron `▸`), Abierto (chevron `▾`, contenido visible).

**Accessibility** ⚠️ **[Recomendado]** — El `<button>` debe declarar `aria-expanded` y `aria-controls`, y el contenido `role="region"`/`aria-labelledby`. Se usa un `id` único por tarjeta. (Las flechas `▸`/`▾` son caracteres legibles, sin significado semántico extra.)

### Navbar (Header)

**Implementado** — `.app-header`: `.brand` (icono + título + subtítulo) + `.header-actions` (`PdfUpload` + `ThemeToggle`).

**Responsive** — En móvil: reduce paddings, oculta `.brand-sub`, compacta botones.

**Accessibility** — `<header>` semántico ✓; botones con `title` ✓.

### Empty State

**Implementado** — `.empty-state` cuando `messages.length === 0`:
- icono emoji `📚`, `h2` "Asistente del Proceso Administrativo", párrafo descriptivo,
- lista `.doc-list` de documentos indexados (si hay),
- `.suggestions` (3 preguntas sugeridas como botones).

**Estados** — Con/sin documentos listados.

**Do** — Centrado, `max-width 560px`, icono 48 px, texto descriptivo `--text-soft`.
**Don't** — No mostrarlo cuando ya hay mensajes.

### Loading Rates

**Implementado:**
1. **Typing indicator** `.typing .dot` ×3 (7 px, `--text-muted`, animación bounce 1.4 s escalonada).
2. **Cursor de streaming** `.cursor` (`▍`, `blink` 1 s, `--accent`), visible mientras `pending && content`.
3. **Progreso de upload** texto `12px --text-muted` "N %".

**[Recomendado]** un spinner genérico (ring) para operaciones de backend distintas del streaming, y esqueletos (skeleton) para cargas de listas.

### Error State

**Parcial** — Errors del chat inline en la burbuja (`⚠️ Error: …`); upload con `.upload-status.error` (`--error`).

**[Recomendado]** una Alert unificada (icono + título + mensaje + `role="alert"`) con variantes `ok | error | info`.

### Progress

**Parcial** — `.progress` (texto "N %") solo en upload.

---

## 5. Estado de componentes vs. plantilla solicitada

| Componente | Estado |
|---|---|
| Button (primario/secundario) | ✅ Implementado (2 variantes) |
| Icon Button | 🟡 Parcialmente implementado (theme, thumbs) |
| Link | ❌ No existe → Recomendado |
| Input (text) | ❌ No existe (solo `textarea`) |
| Textarea | ✅ Implementado (chat composer) |
| Select / Checkbox / Radio / Switch / Search | ❌ No existe → Recomendado |
| Badge / Chip | ✅ Implementado (`doc-item-chunks`, `source-page`) |
| Avatar | ✅ Implementado (círculo emoji en mensajes) |
| Card | 🟡 Parcial — patrón source-card / doc-item |
| Modal / Dialog / Drawer | ❌ No existe → Recomendado |
| Dropdown / Tooltip / Popover | 🟡 Solo tooltip nativo (`title`) |
| Tabs | ❌ No existe |
| Accordion | ✅ Implementado (source-cards) |
| Breadcrumb | ❌ No existe |
| Navbar | ✅ Implementado (header) |
| Sidebar / Pagination / Table / Data Table | ❌ No existe |
| Alert / Toast / Notification | 🟡 Parcial (upload-status) → Recomendado |
| Progress | 🟡 Parcial (upload %) |
| Spinner | ❌ No existe → Recomendado (hay typing) |
| Skeleton | ❌ No existe → Recomendado |
| Empty State | ✅ Implementado |
| Error State | 🟡 Parcial (inline en burbuja / upload) |
| Loading State | ✅ Implementado (typing + cursor) |
| Date Picker / Calendar | ❌ No existe |
| File Upload | ✅ Implementado (PdfUpload) |

---

## 6. Navigation

La app es **single-page, single-view** (sin router):

- **Navbar** = header superior con brand + acciones (upload/tema). No hay menús, tabs, breadcrumbs, sidebar ni paginación.
- **Jerarquía visual:** Cabecera → mensajes (story) → fuentes (acordeón) → compositor/feedback.
- **Móvil:** se oculta `.brand-sub`, se compacta el header; no hay drawer.

**[Recomendado]** si en el futuro hay multi-pantalla: router nativo, header reutilizable, `aria-current="page"` en el nav activo, y drawer categorizado en móvil.

---

## 7. Forms

### Reglas para el único formulario real (chat)
- **Textarea** con `placeholder` + Enter/Shift+Enter + auto-foco.
- **Validación:** texto vacío → no submit (guard `if (!value.trim()) return`).
- **Disable:** mientras `isStreaming`.
- **Errores:** inline (burbuja del asistente) o `.upload-status`.

### Reglas para formularios futuros (Recomendado)
- Cada campo con **label visible** (no solo placeholder).
- Errores con `aria-invalid` y `aria-describedby` asociando el mensaje al campo.
- Campos obligatorios con `required` + `aria-required`.
- Disabled con `opacity: 0.6` y `cursor: not-allowed`.
- Loading: spinner en el botón primario durante submit, botón disabled.
- Formularios grandes: dividir en secciones con heading; errores agrupados en una alert al inicio.

### Correcto vs incorrecto
✅ Correcto: `:focus-visible` ring del accent; error inline junto al campo.
❌ Incorrecto: depender solo del placeholder; errores globales sin asociación al campo.

---

## 8. Tables & Data Visualization

**No existen tablas ni gráficos** en la UI actual.

**[Recomendado]** para una vista de historial/evaluaciones:
- `table` con `thead/th`, `border` solo horizontal, zebra con `--bg-elev`/`--bg-soft`.
- Ordenamiento: header clickeable con flecha de sort + `aria-sort`.
- Estados: empty (empty-state integrado), loading (skeleton rows + overlay), error (alert).
- Paginación "Anterior/Siguiente" con `aria-current` en la página activa.
- Overflow: contenedor con `overflow-x: auto` para anchos < 640 px.

Charts (si se implementan): tokens de color existentes (accent/ok/error/info), leyendas con texto ≥ 4.5:1, ejes con etiquetas descriptivas.

---

## 9. Feedback & States

| Estado | Patrón actual | Tokens |
|---|---|---|
| Loading | typing dots / cursor / "%" upload | `--text-muted`, `--accent` |
| Empty | `.empty-state` | — |
| Error | inline `⚠️ Error:` en burbuja; `.upload-status.error` | `--error` |
| Success | `.upload-status.ok` ("…subido con éxito") | `--ok` |
| Info | `.upload-status.info` ("Subiendo…") | `--info` |
| Confirmación | ❌ "Nueva conversación" no confirma | — |
| Destructive | `clear-btn` (no usa `--error`) | — |

**Inconsistencias:**
1. `thumb-btn.active` usa colores **hardcoded** `#dcfce7` / `#fee2e2`, que rompen el dark mode (ver §16 y §2).
2. "Nueva conversación" (destructivo) no tiene **confirmación** ni estado de error. **[Recomendado]** confirmación inline (2.º clic "¿Seguro?") o modal, y hover hacia `--error`.

**Do** — Patrón de alert unificado por variante; estados que no bloqueen el streaming.
**Don't** — Silenciar errores de carga; los fallos del `rate` se ignoran por diseño (API interna).

---

## 10. Responsive Design

### Mobile (≤ 640 px)
- Header: `padding 10px/14px`, se oculta `.brand-sub`, botones más compactos (12 px, padding `8px 10px`).
- Mensajes: `padding: 16px 12px`, burbujas `max-width: 88%` (vs 78 % desktop).
- Footer: `padding: 12px 14px`.
- Fuentes: `max-height: 240px` con scroll.

### Tablet (640–980 px)
Sin reglas específicas: el diseño es líquido (max-width + `margin: auto`).

### Desktop (≥980 px)
Contenedor centrado en 980 px; header completo con subtítulo visible.

### Large desktop
**[Recomendado]** breakpoint `≥1024 px` manteniendo `max-width: 980px` (sin estirar).

### Reglas globales
- `overflow-y` solo en `.messages` y `.source-content`.
- Nada de `overflow-x` en móvil (truncación con ellipsis).
- Tablas futuras: wrapper scrollable + `min-width: 0` en celdas.

---

## 11. Accessibility (WCAG 2.2 AA)

### Color contrast
- Texto principal y `--text-soft` ✓ AA.
- ⚠️ **Riesgo:** `--text-muted` light (≈2.8:1) en hints de 11–12 px **no** cumple AA. **Recomendado:** `--text-muted` → `#6b7280` y ajustar dark.
- ⚠️ **Botón primario dark:** `#fff` sobre `--accent #4b8bf4` ≈3.3:1 **insuficiente** para 14 px/600. **Recomendado:** texto oscuro sobre accent, o accent más claro en dark (ver §16).

### Focus
- Textarea: ring accent ✓.
- Botones **sin `:focus-visible` explícito**: ❌ → usar el bloque de §4 (Button).

### Keyboard
- Todos los interactivos son `<button>`/`textarea` nativos ✓ (orden de tab natural).
- Acordeón: soporta Enter/Espacio en el `<button>` nativo; falta `aria-expanded`.
- No hay focus traps (no hay modales).

### ARIA (estado actual)
| Elemento | Estado |
|---|---|
| `ThemeToggle` `aria-label` | ✅ |
| `ChatInput` textarea `aria-label` | ❌ |
| `source-header` `aria-expanded`/`aria-controls` | ❌ |
| `.upload-status` `role="status"` | ❌ |
| thumb buttons `aria-pressed` | ❌ |

### Semantic HTML
- `header`/`main`/`form`/`button`/`textarea` ✓; `lang="es"` ✓; todas las interacciones son elementos nativos.

### Touch targets
- Thumbs y clear-btn rondan ~24–30 px < 40 px. **[Recomendado]** mínimo 40–44 px.

### Reduced motion
**No existe** `prefers-reduced-motion`. **[Recomendado]:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Form accessibility & Errors
- Errores inline próximos al campo; los errores del chat deben anunciarse con `role="alert"`. [Recomendado]
- el placeholder es una hint (no una label): añadir labels/`aria-label` a los campos.

---

## 12. Icons

- **No hay librería de iconos.** Los pictogramas son **emojis inline** (`🎓`, `📚`, `📄`, `📑`, `🗑️`, `☀️`, `🌙`, `👍`, `👎`, `🧑🎓`, `🤖`, `⏹`, `➤`).
- Tamaños: por `font-size` (14–18 px); avatares 18 px; cifras grandes en empty 48 px.
- Color: los emojis hay con su propio color (no se tiñen).
- Icon-only buttons: `title` + `aria-label` (⚠️ falta en thumbs).

**Reglas:**
- **No mezclar estilos**: todo emoji o una sola librería SVG (**Recomendado**: `lucide-react`) — nunca ambos.
- Emojis decorativos con `aria-hidden="true"`; si transmiten significado, proporcionar texto alternativo.

---

## 13. Images & Media

- La app **no carga imágenes externas**; no hay `<img>`.
- Avatares: círculo `34px` con emoji sobre `--bg-soft` + borde `--border`.

**[Recomendado]** si se agregan imágenes:
- Aspect ratio 1:1 (avatares), 16:9 (cover cards).
- `border-radius: 8px` (thumbnail) o `--radius` (hero).
- `object-fit: cover`; `loading="lazy"`; `alt` descriptivo (o `alt=""` decorativo).
- Placeholder con skeleton (`--bg-soft` + shimmer).

---

## 14. Motion & Animation

| Animación | Valor actual |
|---|---|
| Transiciones | `0.2s ease` (`--transition`) para background, border-color, color, box-shadow |
| Typing dots | `bounce` 1.4s ease-in-out, escalonado (0.16s / 0.32s) |
| Cursor | `blink` 1s step-end |
| Scroll del chat | `scroll-behavior: smooth` (scrollIntoView) |

**Reglas:**
- 200 ms para microinteracciones (hover/focus).
- 300–400 ms para paneles/modales futuros.
- `prefers-reduced-motion: reduce` → desactivar (ver §11).
- No animar propiedades de layout (solo `transform`/`opacity`).
- Sin animaciones de bucle que distraigan (los dots son pequeños y permitidos).

---

## 15. Content & UX Writing (Español)

- **Botones:** verbos accionables. "Enviar", "Detener", "Subir PDF", "Nueva conversación".
- **Placeholder chat:** "(Enter para enviar, Shift+Enter para salto de línea)".
- **Empty state:** propósito claro + recordatorio de que las respuestas salen de los materiales indexados.
- **Errores:** prefijo "⚠️ Error:" + mensaje concreto (sendos del backend).
- **Hints:** "Basado en N documentos · M fragmentos".
- **Feedback:** "Gracias por tu valoración".
- **Regla:** títulos cortos (≤60 caracteres), lenguaje claro, afirmativo/imperativo, sin spanglish.

---

## 16. Dark Mode

**Implementado** en `[data-theme="dark"]`:
- Fondo: `--bg #0d1117`, superficie `--bg-elev #161b22`, suave `--bg-soft #1c2230`, `--assistant-bubble #161b22`.
- Texto: `#e6edf3` / soft `#adbac7` / muted `#768390`.
- Bordes: `#2a313c`. Acento: `#4b8bf4`, soft `#1c2a44`.
- Feedback:`ok #3fb950`, `error #f85149`, `info #4b8bf4`.

**Inconsistencias/mejoras detectadas:**
1. `--user-bubble` se mantiene `#2563eb` (igual que light) mientras el accent dark es `#4b8bf4`. **[Recomendado]** sincronizar con el accent dark.
2. Thumbs up/down usan `#dcfce7`/`#fee2e2` (fondos claros) en dark → **rompe el tema**. **[Recomendado]** tokens `--ok-soft`/`--error-soft` por tema (o `color-mix()`).
3. `--text-muted` dark (`#768390`, ≈4.7:1) cumple AA ✓.
4. `--accent-contrast #fff` sobre `#4b8bf4` (≈3.3:1) **debajo de AA** → **[Recomendado]** accent más claro (ej. `#5b9cfb`) o texto oscuro.
5. Transición suave al cambiar `background`/`color` en `body` ✓.

---

## 17. Design Patterns

**Implementados:**
- **Chat Q&A con streaming:** pregunta → burbuja de usuario → typing/cursor → respuesta streaming (SSE) → fuentes colapsables → feedback.
- **Upload PDF:** botón → progreso → status (info/success/error).
- **Feedback simple:** thumbs up/down (1 clic) + agradecimiento.
- **Source accordion:** expandir una fuente a la vez.

**Recomendados (para módulos futuros):**
- **CRUD de documentos:** lista + modal de confirmación recuperable.
- **Login** (si se añade auth): formulario simple + error inline + disabled en load.
- **Confirmación destructiva:** modal/dialog + botón "Confirmar" (variante error).
- **Multi-step/wizards,** solo si surge (p. ej. indexación masiva: 1 selección → 2 preferencias → 3 resumen).

**Do** — Reusar `MessageBubble` + `SourceCards` (patrón de burbuja + fuentes) en cualquier char/IA de la app.
**Don't** — No crear pantallas con layouts propietarios fuera del contenedor de 980 px.

---

## 18. Do & Don't (reglas generales)

### Do
- Usar tokens para color/font/radius.
- Patrón único para la acción primaria (estilo `.send-btn` con accent).
- Mostrar cargas, errores, exitos explícitos.
- `aria-label`/`aria-pressed` en botones solo-icono; foco visible en todo interactivo.
- Preferir componentes nativos (button, textarea).

### Don't
- No hardcodear colores (p. ej. `#dcfce7`, `#fee2e2`) fuera de tokens.
- No crear variantes de botón "nuevas" ad hoc.
- No mezclar estilos de iconos (emoji vs librería SVG).
- No depender del `placeholder` como única etiqueta.
- No scrolls internos anidados sin `overflow` controlado.
- No crear un segundo "empty state" distinto del `.empty-state`.

---

## 19. Naming Conventions

| Tipo | Convención | Ejemplos |
|---|---|---|
| Files de componentes | `PascalCase.jsx` | `MessageBubble.jsx` |
| Hooks | `use*` camelCase | `useChat.js`, `useTheme.js` |
| Libs/utils | camelCase `.js` | `api.js` |
| CSS classes | kebab-case | `.send-btn`, `.source-card`, `.upload-status` |
| Tokens | `--kebab-case` | `--bg-elev`, `--accent-soft` |
| States en CSS | sufijos `.ok/.error/.info`, `[data-theme]` | `.upload-status.error` |
| Atributos de contexto | `data-*` | `data-theme` |

**Estructura de carpetas a mantener:**
```
src/
  components/   (presentation/visual)
  hooks/        (useChat, useTheme)
  lib/          (api)
  styles/       (index.css)
```

---

## 20. Implementation Guidelines

1. **Usa tokens siempre:** nada de colores/fonts tipados en componentes; nuevos valores se agregan como token en `index.css` + Change Log.
2. **Composición:** combinar `Bubble + Sources + Feedback` (patrón `MessageBubble`); no duplicar markup.
3. **Prefiere componentes nativos** (button, textarea) antes que wrappers.
4. **Responsive:** usa el breakpoint 640px existente; para nuevas, añade tokens de breakpoint (§2.7) antes de CSS de pantalla.
5. **Accesibilidad:** `:focus-visible` global, `aria-label` en icon-only, `role` de estados.
6. **Otrización del estado con hooks:** `useChat`/`useTheme` centralizan lógica; evita guardar estado en `.css`.
7. **Consistencia:** reutiliza los patrones CSS existentes; si algo se repite 2+ veces, extraer token/componente.

---

## 21. AI Development Rules

Antes de crear o modificar cualquier UI, la IA **debe**:

1. Leer este `DESIGN_SYSTEM.md` y los componentes existentes.
2. Reutilizar componentes existentes (`MessageBubble`, `ChatView`, `PdfUpload`, `ThemeToggle`, etc.) y los selectors de `.css`.
3. Reutilizar design tokens existentes; si introduce un token nuevo, actualizar ambos temas (light/dark) + este documento + Change Log.
4. **Prohibido** estilos arbitrarios o colores hardcoded (inline veces).
5. **No introducir colores sin justificación**; si es estrictamente necesario, validar contraste AA ANTES de agregarlo.
6. No duplicar componentes de funcionalidad ya existente.
7. Mantener responsive (breakpoints existentes).
8. Mantener WCAG 2.2 AA: focus visible, `aria-label` en icon-only, contraste, `role` de estados/loading.
9. Mantener consistencia con las pantallas existentes (español, patrones de título, emojis/mensajes).
10. Mantener/actualizar `DESIGN_SYSTEM.md` + Change Log cuando se introduzcan patrones nuevos.

**Flujo antes de tocar un componente:**
`Explorar (leer selectors/tokens) → Reutilizar → Extend → Variant → Nuevo componente` y documentar.

---

## 22. Component Decision Rules

Prioridad: **Reuse > Extend > Variant > New Component**.

| Situación | Decisión |
|---|---|
| El componente ya cubre la necesidad | **Reuse** |
| Casi sirve, le faltan props/states | **Extend** (añadir props) |
| Distinta variante visual (color/tamaño) | **Variant** (vía tokens si possible) |
| Necesidad nueva clara (single responsibility) | **New Component** |
| Patrón repetido 2+ veces | Extraer a componente reutilizable |

**Reglas de precedencia:**
- No modificar un componente existente si solo se resuelve con variante.
- No crear nueva pantalla con su propio sistema de clases CSS; usar el layout `.app`/`.chat-*`.

---

## 23. Design System Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-08-07 | 1.0.0 | Initial Design System (basado en el estado actual del frontend `web/`) | — |

---

## Annex — Mapas de código

**Tokens (base):** `web/src/styles/index.css:1-50` (light `8-28`, dark `30-50`).
**Layout:** `index.css:71-78` (`.app`), `80-88` (`.app-header`), `189-211` (chat), `532-606` (footer/input).
**Componentes:** `src/components/` (ChatView, ChatInput, MessageBubble, SourceCards, PdfUpload, ThemeToggle); hooks `src/hooks/`; gestión `src/lib/api.js`.

**Stack Web:** React 18.3 + react-dom 18.3, Vite 5, CSS vanilla con variables, sin Tailwind/TS/router. Las ampliaciones deben mantener este stack (JSX, CSS con variables, componentes React).