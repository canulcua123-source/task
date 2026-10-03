# Sistema de Tareas Escolares — UTM

## Qué es
Herramienta para gestionar tareas escolares de Jesús Guadalupe Canul (UTM, TI Innovación Digital, 7° cuatrimestre, grupo A).

## Estructura
- `config.json` — datos del estudiante, escuela, asignaturas y formato
- `tareas_db.json` — base de datos de tareas
- `gestor.py` — motor principal (gestión + generación de Word + orquestación)
- `generar_pdf.py` — pipeline portada PIL→HTML→PDF con Playwright
- `revisor.py` — validador automático de calidad (APA, estructura, palabras)
- `organizar.py` — gestión de carpetas por asignatura
- `teams.py` — integración con Microsoft Teams vía Graph API
- `assets/` — logo UTM y recursos
- `sandbox/entregas/` — documentos organizados por carpeta de asignatura

## Carpetas de entregas
```
sandbox/entregas/
├── Etica y Legislacion en TI/
├── Base de Datos en la Nube/
├── Fundamentos de IA/
└── (archivos sueltos se mueven con: python organizar.py mover)
```
Para crear/verificar carpetas: `python organizar.py setup`

## Uso agéntico (cómo debe actuar Claude)

### REGLA: Siempre confirmar asignatura
Antes de registrar cualquier tarea, confirmar de qué materia es. Si la imagen/instrucción lo menciona claramente, usarla sin preguntar.

### Orquestación: cuando el usuario asigne una tarea
Claude debe dividir y ejecutar el trabajo automáticamente usando subagentes en paralelo cuando sea posible:

1. **Analizar** qué se pide (leer instrucciones de Teams o lo que diga el usuario)
2. **Registrar** la tarea en `tareas_db.json` con `agregar_tarea()` o `importar_desde_teams()`
3. **Investigar** el tema lanzando subagentes de investigación en paralelo (ver sección Orquestación con Subagentes)
4. **Escribir** el contenido completo en el campo `contenido` (array de secciones)
5. **Generar PDF**: `python generar_pdf.py <id>` (pipeline: portada PIL → HTML → PDF Playwright)
6. **Revisar calidad**: `python revisor.py <id>` — valida estructura, palabras, APA, archivo
7. **Corregir** si el revisor reporta fallas → arreglar y regenerar
8. **Organizar**: mover PDF a carpeta de asignatura correspondiente
9. **Subir a Teams** si el usuario lo pide
10. **Marcar como completada/entregada**

No preguntar "¿continúo?" entre pasos — ejecutar el flujo completo y reportar al final.

### REGLA: Review obligatorio al final de cada tarea
Usar `python gestor.py flujo <id>` que ejecuta el pipeline completo:
PDF → Review → Organizar carpeta → Marcar completada

Si el review reporta fallas, corregir con:
```python
# Desde código Python:
gestor.actualizar_contenido(id, contenido_corregido)

# Desde CLI (regenerar tras corrección):
python gestor.py flujo <id>
```

Criterios custom por tarea (ejemplo 1500 palabras):
```bash
python revisor.py <id> --criterios '{"min_palabras": 1400, "max_palabras": 1600}'
```

### Modo JSON para parsing agéntico
Todos los CLIs soportan `--json` para output estructurado:
```bash
python gestor.py resumen --json
python gestor.py alertas --json
python revisor.py <id> --json
python organizar.py estado --json
```

### Cuando el usuario diga "revisa mis tareas":
1. Ejecutar `python gestor.py alertas` para ver vencidas/próximas
2. Ejecutar `python gestor.py resumen` para el estado general
3. Mostrar resumen: pendientes, alertas de vencimiento, por asignatura

### Cuando el usuario diga "revisa mis tareas de Teams":
1. Ejecutar `python teams.py revisar` para obtener tareas pendientes
2. Comparar contra `tareas_db.json` para ver cuáles ya están registradas
3. Mostrar resumen: qué falta, fechas, estado
4. Si el usuario pide hacer una tarea → ejecutar flujo completo (pasos 1-8 arriba)

### Generación por lotes:
- `python gestor.py pendientes` — genera documentos para TODAS las tareas pendientes con contenido
- Útil cuando hay varias tareas acumuladas

### Funciones disponibles en gestor.py:
| Función | Qué hace |
|---|---|
| `agregar_tarea(clave, titulo, desc, fecha, contenido)` | Crea tarea en DB |
| `actualizar_contenido(id, contenido)` | Actualiza contenido tras revisión |
| `actualizar_estado(id, estado)` | Cambia estado |
| `importar_desde_teams(teams_data, clave)` | Importa tarea de Teams a DB |
| `flujo_completo(id, criterios_review=)` | Pipeline: PDF → Review → Organizar → Completar |
| `generar_documento(id)` | Genera Word con portada UTM (legacy) |
| `generar_pendientes()` | Genera docs para todas las pendientes |
| `alertas_vencidas()` | Lista tareas próximas a vencer (≤3 días) o vencidas |
| `resumen_tareas()` | Resumen para uso agéntico |

### CLI de gestor.py:
```
python gestor.py listar [estado] [asignatura]
python gestor.py resumen
python gestor.py agregar <clave> <titulo> [fecha]
python gestor.py estado <id> <nuevo_estado>
python gestor.py generar <id>
python gestor.py pendientes
python gestor.py alertas
python gestor.py flujo <id>
python gestor.py asignaturas
```

### Funciones disponibles en teams.py:
| Función | Qué hace |
|---|---|
| `obtener_tareas_estructuradas()` | Devuelve lista limpia de tareas de Teams (bridge a gestor) |
| `subir_archivo(class_id, assignment_id, ruta)` | Sube archivo a submission |
| `entregar_tarea(class_id, assignment_id)` | Submit/turn-in |

### CLI de teams.py:
```
python teams.py login
python teams.py revisar
python teams.py detalle <class_id> <assignment_id>
python teams.py subir <class_id> <assignment_id> <ruta>
python teams.py entregar <class_id> <assignment_id>
```

## Preview Dashboard (preview.py)
Dashboard visual que muestra el estado de cada tarea y qué necesita cada agente.

### CLI de preview.py:
```
python preview.py <id>              # Dashboard completo (portada + contenido + review + agentes)
python preview.py <id> portada      # Solo campos de portada
python preview.py <id> contenido    # Outline con conteo de palabras por sección
python preview.py <id> review       # Review de calidad con colores
python preview.py <id> agentes      # Panel de agentes con instrucciones específicas
python preview.py pipeline <id>     # Ejecuta pipeline con status en vivo
```

### Cuándo usar el preview:
- **Antes de generar**: `preview.py <id> portada` para verificar que todos los datos estén bien
- **Después de escribir contenido**: `preview.py <id> contenido` para ver outline y palabras
- **Después de generar**: `preview.py <id> agentes` para ver qué falta corregir
- **Flujo completo visual**: `preview.py pipeline <id>` para ver el pipeline ejecutándose

### Panel de agentes — qué hace cada uno:
| Agente | Responsabilidad | Archivos que toca |
|---|---|---|
| Portada | Logo, datos del alumno, fecha | `config.json`, `assets/` |
| Investigador | Buscar fuentes, ampliar contenido | `tareas_db.json` → contenido |
| Redactor | Estructura, intro, conclusión, coherencia | `tareas_db.json` → contenido[] |
| Revisor | APA, palabras, formato, validación | `revisor.py` |
| Organizador | Carpetas, mover archivos | `organizar.py`, `sandbox/entregas/` |

Cada agente reporta: OK, REQUIERE ACCIÓN o FALLAS DETECTADAS, con instrucciones exactas de qué arreglar y dónde.

## Formato de contenido en tareas
El campo `contenido` es un array de secciones:
```json
[
  {"tipo": "titulo", "texto": "Introducción"},
  {"tipo": "parrafo", "texto": "Texto del párrafo..."},
  {"tipo": "subtitulo", "texto": "Sección 2"},
  {"tipo": "lista", "items": ["Item 1", "Item 2"]}
]
```
**Nota:** Si `contenido` es un string (como en tareas tipo foro), no se genera Word.

## Generación de PDF desde HTML
Para tareas que requieren diseño visual (carteles, infografías):
1. Crear HTML con estilos inline
2. Convertir con Playwright:
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{html_path}")
    page.wait_for_timeout(3000)
    page.pdf(path=pdf_path, format="Letter", print_background=True,
             margin={"top":"0","right":"0","bottom":"0","left":"0"})
    browser.close()
```

## Orquestación con Subagentes

### Cuándo usar subagentes
- **Tareas largas (>1000 palabras)**: dividir investigación en subtemas, un subagente por tema
- **Tareas con múltiples secciones independientes**: cada subagente redacta una sección
- **Investigación intensiva**: lanzar subagentes WebSearch en paralelo por tema
- **Revisión**: un subagente revisa formato mientras otro revisa contenido

### Arquitectura de subagentes para tareas grandes

```
┌─────────────────────────────────────────────────┐
│              ORQUESTADOR (Claude)                │
│  1. Analiza la tarea y divide en subtareas       │
│  2. Lanza subagentes en paralelo                 │
│  3. Consolida resultados                         │
│  4. Genera PDF + Review                          │
└───────┬──────────┬──────────┬───────────────────┘
        │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼──────┐
   │ INVEST │ │ INVEST │ │ INVEST  │  ← Fase 1: Investigación paralela
   │ Tema A │ │ Tema B │ │ Tema C  │
   └────┬───┘ └───┬────┘ └──┬──────┘
        │         │         │
   ┌────▼─────────▼─────────▼──────┐
   │     REDACTOR (Claude main)     │  ← Fase 2: Unifica y redacta
   │  Consolida, da coherencia,     │
   │  ajusta extensión y tono       │
   └────────────┬──────────────────┘
                │
   ┌────────────▼──────────────────┐
   │     REVISOR (python revisor.py)│  ← Fase 3: QA automático
   │  + subagente de revisión crít. │
   │  Estructura, APA, palabras,    │
   │  coherencia, criterios custom  │
   └────────────┬──────────────────┘
                │ ¿Pasa? → PDF final
                │ ¿Falla? → Vuelve a Fase 2
```

### Prompt template para subagente investigador
Cuando lances un subagente de investigación, usa este formato:
```
Investiga sobre [TEMA ESPECÍFICO] para una tarea universitaria de [MATERIA].
Nivel: universitario, 7° cuatrimestre de TI.
Necesito:
- Datos concretos con fuentes citables (autor, año)
- Ejemplos reales o casos de estudio
- Información actual (preferir fuentes 2022-2026)
Formato de salida: texto corrido, ~[N] palabras, sin formato markdown.
Incluye al final las referencias en formato APA 7.
```

### Prompt template para subagente revisor
```
Revisa el siguiente contenido de tarea universitaria contra estos criterios:
- Extensión: [min]-[max] palabras
- Formato: referencias en APA 7
- Estructura: introducción, desarrollo con subtemas, conclusión, referencias
- Coherencia: transiciones entre secciones, hilo argumentativo
- Nivel académico: universitario (7° cuatrimestre TI)
- Fuente: Arial 12pt (verificar que el contenido no asuma otro formato)
Reporta: qué cumple, qué falta, qué corregir. Sé específico.
```

### Generación de imágenes locales
Para tareas que requieran imágenes (diagramas, infografías, carteles):
- **Diagramas**: generar con PIL/Pillow directamente en Python
- **Portadas**: ya generadas automáticamente por `gestor._crear_portada_imagen()`
- **Gráficos**: usar matplotlib si se necesitan gráficas
- **Carteles/Infografías**: generar HTML con diseño visual → Playwright → PDF

### CLI de revisor.py:
```
python revisor.py <id>                              # Revisa una tarea
python revisor.py <id> --criterios '{"min_palabras": 1500}'  # Criterios custom
python revisor.py todos                             # Revisa todas las activas
```

### CLI de organizar.py:
```
python organizar.py setup     # Crea carpetas por asignatura
python organizar.py mover     # Mueve archivos sueltos a sus carpetas
python organizar.py estado    # Muestra estado de organización
python organizar.py limpiar   # Elimina archivos temporales
```

## Archivos sensibles (NO commitear)
- `.token_cache.json` — tokens de Microsoft
- `.teams_session_*` — sesiones de Chromium (agregar a .gitignore)

## Entorno
- Python venv en `.venv/`
- Activar: `source .venv/bin/activate`
- Dependencias: python-docx, fpdf2, rich, click, msal, requests, Pillow, playwright
