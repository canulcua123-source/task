# Sistema de Tareas Escolares — UTM

## Qué es
Herramienta para gestionar tareas escolares de Jesús Guadalupe Canul (UTM, TI Innovación Digital, 7° cuatrimestre, grupo A).

## Estructura
- `config.json` — datos del estudiante, escuela, asignaturas y formato
- `tareas_db.json` — base de datos de tareas
- `gestor.py` — motor principal (gestión + generación de Word + orquestación)
- `teams.py` — integración con Microsoft Teams vía Graph API
- `assets/` — logo UTM y recursos
- `entregas/` — documentos Word/PDF generados

## Uso agéntico (cómo debe actuar Claude)

### Orquestación: cuando el usuario asigne una tarea
Claude debe dividir y ejecutar el trabajo automáticamente:

1. **Analizar** qué se pide (leer instrucciones de Teams o lo que diga el usuario)
2. **Registrar** la tarea en `tareas_db.json` con `agregar_tarea()` o `importar_desde_teams()`
3. **Investigar** el tema si es necesario (WebSearch/WebFetch)
4. **Escribir** el contenido completo en el campo `contenido` (array de secciones)
5. **Generar** el documento: `python gestor.py generar <id>` o `flujo_completo(id)`
6. **Convertir a PDF** si se necesita (Playwright para HTML, o docx2pdf)
7. **Subir a Teams** si el usuario lo pide
8. **Marcar como completada/entregada**

No preguntar "¿continúo?" entre pasos — ejecutar el flujo completo y reportar al final.

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
- `python gestor.py pendientes` — genera Word para TODAS las tareas pendientes con contenido
- Útil cuando hay varias tareas acumuladas

### Funciones disponibles en gestor.py:
| Función | Qué hace |
|---|---|
| `agregar_tarea(clave, titulo, desc, fecha, contenido)` | Crea tarea en DB |
| `importar_desde_teams(teams_data, clave)` | Importa tarea de Teams a DB |
| `generar_documento(id)` | Genera Word con portada UTM |
| `generar_pendientes()` | Genera Word para todas las pendientes |
| `alertas_vencidas()` | Lista tareas próximas a vencer (≤3 días) o vencidas |
| `flujo_completo(id)` | Orquesta: generar → devolver ruta |
| `actualizar_estado(id, estado)` | Cambia estado |
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

## Archivos sensibles (NO commitear)
- `.token_cache.json` — tokens de Microsoft
- `.teams_session_*` — sesiones de Chromium (agregar a .gitignore)

## Entorno
- Python venv en `.venv/`
- Activar: `source .venv/bin/activate`
- Dependencias: python-docx, fpdf2, rich, click, msal, requests, Pillow, playwright
