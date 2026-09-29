# Task — Sistema de Tareas Escolares UTM

Sistema agéntico para gestionar tareas escolares, generar documentos con portada institucional y sincronizar con Microsoft Teams.

## Arquitectura

```
task/
├── gestor.py              # Motor principal: CRUD de tareas, generación Word, orquestación
├── teams.py               # Integración Microsoft Teams vía Graph API
├── config.json            # Datos del estudiante, escuela, asignaturas, formato
├── tareas_db.json         # Base de datos de tareas (JSON)
├── CLAUDE.md              # Instrucciones agénticas para Claude Code
├── .gitignore
├── assets/                # Logo UTM y recursos
└── sandbox/               # Workspace local (no se sube al repo)
    └── entregas/          # Documentos generados (Word, PDF, HTML)
```

## Funcionalidades

### Gestión de tareas
- Crear, listar, filtrar y actualizar tareas por asignatura
- Alertas de vencimiento (tareas a ≤3 días o vencidas)
- Importar tareas desde Microsoft Teams

### Generación de documentos
- Word con portada institucional UTM (barras azules, logo, datos del alumno)
- Soporte para títulos, subtítulos, párrafos y listas
- Generación por lotes de todas las tareas pendientes
- HTML a PDF con Playwright (para carteles e infografías)

### Integración Teams
- Autenticación vía device code flow (MSAL)
- Listar clases y tareas pendientes
- Subir archivos y entregar tareas
- Bridge automático Teams → DB local

## Uso

```bash
# Activar entorno
source .venv/bin/activate

# Gestión de tareas
python gestor.py listar
python gestor.py alertas
python gestor.py resumen
python gestor.py agregar <asignatura> <titulo> [fecha]
python gestor.py generar <id>
python gestor.py pendientes          # genera Word para todas las pendientes
python gestor.py flujo <id> [--teams] # orquesta: generar → completar → subir

# Teams
python teams.py login                # primera vez
python teams.py revisar              # ver tareas pendientes
python teams.py subir <class> <assignment> <archivo>
python teams.py entregar <class> <assignment>
```

## Flujo agéntico (Claude Code)

Cuando se asigna una tarea, Claude orquesta automáticamente:

1. **Analizar** instrucciones (Teams o usuario)
2. **Registrar** en `tareas_db.json`
3. **Investigar** el tema si es necesario
4. **Escribir** contenido (array de secciones)
5. **Generar** documento Word con portada UTM
6. **Convertir** a PDF si se necesita
7. **Subir** a Teams (opcional)
8. **Marcar** como completada/entregada

## Formato de contenido

```json
[
  {"tipo": "titulo", "texto": "Introducción"},
  {"tipo": "parrafo", "texto": "Texto del párrafo..."},
  {"tipo": "subtitulo", "texto": "Sección 2"},
  {"tipo": "lista", "items": ["Item 1", "Item 2"]}
]
```

## Requisitos

```
python-docx  Pillow  msal  requests  playwright  rich  click
```

## Sandbox

El directorio `sandbox/` es el workspace local donde se guardan las entregas generadas. No se sube al repositorio — cada instalación genera sus propios documentos.
