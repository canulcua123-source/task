# Sistema Agéntico UTM — Arquitectura

Cómo funciona el sistema de tareas escolares con agentes autónomos: pipeline, review y orquestación paralela.

## Pipeline completo

```mermaid
flowchart TD
    A["1. Analizar\n(Imagen / texto / Teams)"] --> B["2. Registrar\n(tareas_db.json)"]
    B --> C["3. Investigar\n(Subagentes paralelos)"]
    C --> D["4. Redactar\n(contenido[])"]
    D --> E["5. Generar PDF\n(Playwright HTML→PDF)"]
    E --> F{"Review OK?\n(revisor.py)"}
    F -->|SI| G["Organizar\n(Carpeta asignatura)"]
    F -->|NO| H["Corregir"]
    H -->|regenerar| D
    G --> I["✅ Completada"]

    style A fill:#f5f5f5,stroke:#333
    style B fill:#f5f5f5,stroke:#333
    style C fill:#e8f0fe,stroke:#1a73e8
    style D fill:#e8f0fe,stroke:#1a73e8
    style E fill:#f5f5f5,stroke:#333
    style F fill:#fff3e0,stroke:#e65100
    style G fill:#e8f5e9,stroke:#2e7d32
    style H fill:#fce4ec,stroke:#c62828
    style I fill:#e8f5e9,stroke:#2e7d32
```

Un solo comando ejecuta todo: analiza la tarea, la registra, investiga con subagentes en paralelo, redacta el contenido, genera el PDF con Playwright, pasa el review automático y organiza el archivo en la carpeta de su asignatura. Si el review falla, corrige y regenera hasta que pase.

```bash
python gestor.py flujo <id>           # Pipeline completo
python preview.py pipeline <id>       # Pipeline con status visual
```

## Panel de agentes

```mermaid
flowchart TB
    subgraph orq["ORQUESTADOR (Claude Code)"]
        direction LR
        P["🎨 Portada\n─────────\nconfig.json\nassets/logo\n─────────\nLogo, datos\nalumno, fecha"]
        I["🔍 Investigador\n─────────\nWebSearch\nWebFetch\n─────────\nFuentes APA 7\ndatos y casos"]
        R["✍️ Redactor\n─────────\ntareas_db.json\ncontenido[]\n─────────\nIntro, desarrollo\nconclusión"]
        V["🔎 Revisor\n─────────\nrevisor.py\ngenerar_pdf.py\n─────────\nAPA, palabras\nestructura"]
        O["📁 Organizador\n─────────\norganizar.py\nsandbox/entregas/\n─────────\nCarpetas por\nasignatura"]
    end

    orq --> D["preview.py — Dashboard visual\nPortada · Contenido · Review · Panel de agentes"]

    style P fill:#e3f2fd,stroke:#1565c0
    style I fill:#e8f0fe,stroke:#1a73e8
    style R fill:#f3e5f5,stroke:#7b1fa2
    style V fill:#fff3e0,stroke:#e65100
    style O fill:#e0f2f1,stroke:#00695c
    style D fill:#e8f0fe,stroke:#1a73e8
```

Cada agente reporta su estado (**OK**, **Requiere acción**, **Fallas**) con instrucciones exactas de qué arreglar y en qué archivo. El Revisor es la compuerta: si detecta fallas, el Redactor recibe instrucciones específicas de qué corregir, y el pipeline vuelve a generar.

```bash
python preview.py <id> agentes    # Ver estado de cada agente
```

## Orquestación con subagentes

```mermaid
flowchart TD
    DIV["Dividir en subtemas"] --> |"EN PARALELO"| SA["Subagente A\nInvestiga tema 1"]
    DIV --> SB["Subagente B\nInvestiga tema 2"]
    DIV --> SC["Subagente C\nInvestiga tema 3"]

    SA --> CON["Consolidar y redactar\nUnifica, da coherencia, ajusta extensión"]
    SB --> CON
    SC --> CON

    CON --> REV{"Review?"}
    REV -->|PASA| FIN["PDF y Organizar\nCarpeta asignatura → completada"]
    REV -->|FALLA| CON

    style DIV fill:#f5f5f5,stroke:#333
    style SA fill:#e8f0fe,stroke:#1a73e8
    style SB fill:#e8f0fe,stroke:#1a73e8
    style SC fill:#e8f0fe,stroke:#1a73e8
    style CON fill:#f3e5f5,stroke:#7b1fa2
    style REV fill:#fff3e0,stroke:#e65100
    style FIN fill:#e8f5e9,stroke:#2e7d32
```

Para tareas de más de 1,000 palabras, el orquestador divide el tema en subtemas y lanza un subagente de investigación por cada uno en paralelo. Los resultados se consolidan en una redacción coherente, y el revisor valida contra los criterios de evaluación. Si falla, el loop corrige y regenera hasta que pase.

| Fase | Qué hace | Herramienta |
|---|---|---|
| 1. Investigación | Subagentes buscan fuentes por subtema | Agent tool + WebSearch |
| 2. Redacción | Unifica hallazgos, ajusta tono y extensión | Claude main + gestor.py |
| 3. QA | Valida APA, estructura, palabras, archivo | revisor.py + preview.py |

## Herramientas CLI

| Comando | Qué hace |
|---|---|
| `python gestor.py flujo <id>` | Pipeline completo: PDF → Review → Organizar → Completar |
| `python gestor.py resumen --json` | Estado de todas las tareas (JSON) |
| `python gestor.py alertas --json` | Tareas próximas a vencer (JSON) |
| `python generar_pdf.py <id>` | Solo generar PDF (portada PIL → HTML → Playwright) |
| `python revisor.py <id>` | Solo review de calidad |
| `python revisor.py <id> --json` | Review en JSON para parsing agéntico |
| `python organizar.py setup` | Crear carpetas por asignatura |
| `python organizar.py mover` | Mover archivos sueltos a sus carpetas |
| `python organizar.py estado --json` | Estado de organización (JSON) |
| `python preview.py <id>` | Dashboard visual completo |
| `python preview.py <id> agentes` | Panel de agentes con instrucciones |
| `python preview.py pipeline <id>` | Pipeline en vivo con barra de progreso |
