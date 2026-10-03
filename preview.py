#!/usr/bin/env python3
"""
Preview Dashboard — Vista en vivo del estado de tareas y agentes.
Muestra portada, contenido, review y da instrucciones específicas a cada agente.

Uso:
  python preview.py <tarea_id>          # Preview completo de una tarea
  python preview.py <tarea_id> portada  # Solo preview de portada
  python preview.py <tarea_id> contenido # Solo preview de contenido
  python preview.py <tarea_id> agentes  # Muestra instrucciones para agentes
  python preview.py pipeline <tarea_id> # Simula el pipeline con status en vivo
"""

import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

import gestor

console = Console()


# ─── PORTADA PREVIEW ────────────────────────────────────────

def preview_portada(tarea):
    """Muestra un preview textual de la portada."""
    config = gestor.load_config()
    est = config["estudiante"]
    esc = config["escuela"]
    logo_path = BASE_DIR / esc.get("logo", "")

    campos = [
        ("Universidad", esc["nombre"]),
        ("Carrera", est["carrera"]),
        ("Logo", f"{'OK' if logo_path.exists() else 'NO ENCONTRADO'} ({logo_path.name})"),
        ("", ""),
        ("Actividad", tarea["titulo"]),
        ("Materia", tarea["asignatura"]),
        ("Maestro", tarea["maestro"]),
        ("Integrantes", est["nombre"]),
        ("Grado", est["cuatrimestre"]),
        ("Grupo", est["grupo"]),
        ("Fecha entrega", tarea.get("fecha_entrega") or "Sin fecha"),
    ]

    table = Table(
        show_header=False,
        box=box.DOUBLE_EDGE,
        border_style="blue",
        padding=(0, 2),
        title="[bold blue]PORTADA UTM[/]",
        title_style="bold blue",
        width=60,
    )
    table.add_column("Campo", style="bold cyan", width=16)
    table.add_column("Valor", style="white")

    for campo, valor in campos:
        if not campo:
            table.add_row("", "")
        else:
            # Marcar campos vacíos o problemáticos
            estilo = "white"
            if not valor or valor == "Sin fecha":
                estilo = "yellow"
                valor = f"{valor} ⚠"
            if "NO ENCONTRADO" in str(valor):
                estilo = "red"
                valor = f"{valor} ❌"
            table.add_row(campo, f"[{estilo}]{valor}[/]")

    return table


# ─── CONTENIDO PREVIEW ─────────────────────────────────────

def preview_contenido(tarea):
    """Muestra un outline del contenido con conteo de palabras por sección."""
    contenido = tarea.get("contenido", [])

    if not isinstance(contenido, list) or not contenido:
        return Panel("[yellow]Sin contenido estructurado[/]", title="Contenido")

    tree = Tree("[bold blue]Contenido[/]", guide_style="blue")
    total_palabras = 0
    seccion_actual = None

    for i, sec in enumerate(contenido):
        tipo = sec.get("tipo", "")
        texto = sec.get("texto", "")

        if tipo == "titulo":
            seccion_actual = tree.add(f"[bold cyan]{texto}[/]")

        elif tipo == "subtitulo":
            nodo = seccion_actual or tree
            seccion_actual_sub = nodo.add(f"[cyan]{texto}[/]")

        elif tipo == "parrafo":
            palabras = len(texto.split())
            total_palabras += palabras
            nodo = seccion_actual or tree
            # Mostrar preview truncado
            preview = texto[:80] + "..." if len(texto) > 80 else texto
            color = "green" if palabras >= 30 else "yellow" if palabras >= 10 else "red"
            nodo.add(f"[dim]{preview}[/] [{color}]({palabras}w)[/]")

        elif tipo == "lista":
            items = sec.get("items", [])
            palabras_lista = sum(len(it.split()) for it in items)
            total_palabras += palabras_lista
            nodo = seccion_actual or tree
            lista_nodo = nodo.add(f"[dim]Lista ({len(items)} items, {palabras_lista}w)[/]")
            for item in items[:3]:
                item_preview = item[:60] + "..." if len(item) > 60 else item
                lista_nodo.add(f"[dim]• {item_preview}[/]")
            if len(items) > 3:
                lista_nodo.add(f"[dim]... +{len(items) - 3} más[/]")

    tree.add(f"\n[bold white]Total: {total_palabras} palabras[/]")
    return tree


# ─── REVIEW PREVIEW ─────────────────────────────────────────

def preview_review(tarea_id):
    """Ejecuta el review y muestra resultados con colores."""
    import revisor

    reporte = revisor.revisar_tarea(tarea_id)
    if "error" in reporte:
        return Panel(f"[red]{reporte['error']}[/]", title="Review")

    table = Table(
        title="[bold]Review de Calidad[/]",
        box=box.ROUNDED,
        border_style="blue",
    )
    table.add_column("Check", style="white", width=25)
    table.add_column("Estado", width=8, justify="center")
    table.add_column("Detalle", style="dim")

    iconos = {"OK": "[green]✅ OK[/]", "FALLA": "[red]❌ FAIL[/]", "ADVERTENCIA": "[yellow]⚠ WARN[/]", "N/A": "[dim]➖ N/A[/]"}

    for check in reporte["checks"]:
        estado = iconos.get(check["estado"], "?")
        detalle = check.get("detalle", "")
        table.add_row(check["check"], estado, detalle)

    # Línea de veredicto
    v = reporte["veredicto"]
    color = "green" if v == "APROBADO" else "red"
    r = reporte["resumen"]
    table.add_section()
    table.add_row(
        f"[bold {color}]{v}[/]",
        "",
        f"✅ {r['ok']}  ⚠️ {r['advertencias']}  ❌ {r['fallas']}  |  {reporte['palabras']}w"
    )

    return table


# ─── AGENTES: INSTRUCCIONES ESPECÍFICAS ─────────────────────

def generar_instrucciones_agentes(tarea_id):
    """Genera instrucciones específicas para cada agente según el estado de la tarea."""
    import revisor

    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        return Panel("[red]Tarea no encontrada[/]", title="Agentes")

    reporte = revisor.revisar_tarea(tarea_id)
    config = gestor.load_config()
    contenido = tarea.get("contenido", [])

    agentes = []

    # ── Agente de Portada ──
    portada_issues = []
    logo_path = BASE_DIR / config["escuela"].get("logo", "")
    if not logo_path.exists():
        portada_issues.append("Logo UTM no encontrado — colocar en assets/logo_utm.png")
    if not tarea.get("fecha_entrega"):
        portada_issues.append("Sin fecha de entrega — agregar para que aparezca en portada")

    if portada_issues:
        agentes.append({
            "nombre": "Agente Portada",
            "icono": "🎨",
            "estado": "REQUIERE ACCIÓN",
            "color": "yellow",
            "archivos": ["config.json", "assets/logo_utm.png"],
            "instrucciones": portada_issues,
        })
    else:
        agentes.append({
            "nombre": "Agente Portada",
            "icono": "🎨",
            "estado": "OK",
            "color": "green",
            "archivos": ["gestor.py:_crear_portada_imagen()"],
            "instrucciones": ["Portada completa — logo, datos, formato correctos"],
        })

    # ── Agente de Investigación ──
    n_palabras = reporte.get("palabras", 0)
    tiene_refs = any(
        c["check"] == "Referencias" and c["estado"] == "OK"
        for c in reporte.get("checks", [])
    )
    inv_issues = []
    if n_palabras < 300:
        inv_issues.append(f"Contenido muy corto ({n_palabras}w) — investigar más sobre el tema")
    if not tiene_refs:
        inv_issues.append("Faltan referencias — buscar fuentes académicas (APA 7)")

    if inv_issues:
        agentes.append({
            "nombre": "Agente Investigador",
            "icono": "🔍",
            "estado": "REQUIERE ACCIÓN",
            "color": "yellow",
            "archivos": ["tareas_db.json → contenido"],
            "instrucciones": inv_issues,
        })
    else:
        agentes.append({
            "nombre": "Agente Investigador",
            "icono": "🔍",
            "estado": "OK",
            "color": "green",
            "archivos": [],
            "instrucciones": [f"Contenido suficiente ({n_palabras}w) con referencias"],
        })

    # ── Agente Redactor ──
    estructura_issues = []
    for check in reporte.get("checks", []):
        if check["estado"] == "FALLA" and check["check"] in ("Introducción", "Conclusión", "Secciones principales"):
            estructura_issues.append(f"{check['check']}: {check.get('detalle', 'falta')}")

    # Buscar párrafos cortos
    for check in reporte.get("checks", []):
        if "muy corto" in check.get("check", "").lower():
            estructura_issues.append(f"{check['check']}: {check.get('detalle', '')}")

    if estructura_issues:
        agentes.append({
            "nombre": "Agente Redactor",
            "icono": "✍️",
            "estado": "REQUIERE ACCIÓN",
            "color": "yellow",
            "archivos": ["tareas_db.json → contenido[]"],
            "instrucciones": estructura_issues,
        })
    else:
        agentes.append({
            "nombre": "Agente Redactor",
            "icono": "✍️",
            "estado": "OK",
            "color": "green",
            "archivos": [],
            "instrucciones": ["Estructura completa: intro + desarrollo + conclusión + refs"],
        })

    # ── Agente Revisor ──
    fallas = [c for c in reporte.get("checks", []) if c["estado"] == "FALLA"]
    adverts = [c for c in reporte.get("checks", []) if c["estado"] == "ADVERTENCIA"]

    if fallas:
        agentes.append({
            "nombre": "Agente Revisor",
            "icono": "🔎",
            "estado": "FALLAS DETECTADAS",
            "color": "red",
            "archivos": ["revisor.py"],
            "instrucciones": [f"❌ {f['check']}: {f.get('detalle', '')}" for f in fallas],
        })
    elif adverts:
        agentes.append({
            "nombre": "Agente Revisor",
            "icono": "🔎",
            "estado": "ADVERTENCIAS",
            "color": "yellow",
            "archivos": ["revisor.py"],
            "instrucciones": [f"⚠ {a['check']}: {a.get('detalle', '')}" for a in adverts],
        })
    else:
        agentes.append({
            "nombre": "Agente Revisor",
            "icono": "🔎",
            "estado": "APROBADO",
            "color": "green",
            "archivos": ["revisor.py"],
            "instrucciones": ["Todos los checks pasaron"],
        })

    # ── Agente Organizador ──
    import organizar
    carpeta = organizar.obtener_carpeta(tarea["asignatura_clave"])
    archivo = tarea.get("archivo_generado")

    org_issues = []
    if not carpeta.exists():
        org_issues.append(f"Crear carpeta: {carpeta.name}/")
    if archivo and not Path(archivo).exists():
        org_issues.append(f"Archivo generado no encontrado: {archivo}")
    if not archivo:
        org_issues.append("No se ha generado archivo aún")

    if org_issues:
        agentes.append({
            "nombre": "Agente Organizador",
            "icono": "📁",
            "estado": "REQUIERE ACCIÓN",
            "color": "yellow",
            "archivos": ["organizar.py", str(carpeta)],
            "instrucciones": org_issues,
        })
    else:
        agentes.append({
            "nombre": "Agente Organizador",
            "icono": "📁",
            "estado": "OK",
            "color": "green",
            "archivos": [str(carpeta)],
            "instrucciones": [f"Archivo en {carpeta.name}/"],
        })

    return agentes


def mostrar_agentes(tarea_id):
    """Renderiza el panel de agentes."""
    agentes = generar_instrucciones_agentes(tarea_id)

    panels = []
    for ag in agentes:
        color = ag["color"]
        contenido_lines = []

        contenido_lines.append(f"[bold {color}]{ag['estado']}[/]\n")

        if ag["archivos"]:
            contenido_lines.append("[dim]Archivos:[/]")
            for f in ag["archivos"]:
                contenido_lines.append(f"  [dim cyan]{f}[/]")
            contenido_lines.append("")

        contenido_lines.append("[dim]Instrucciones:[/]")
        for inst in ag["instrucciones"]:
            contenido_lines.append(f"  {inst}")

        panel = Panel(
            "\n".join(contenido_lines),
            title=f"{ag['icono']} {ag['nombre']}",
            border_style=color,
            width=50,
            padding=(1, 2),
        )
        panels.append(panel)

    return panels


# ─── PIPELINE LIVE ──────────────────────────────────────────

def pipeline_live(tarea_id):
    """Muestra el pipeline ejecutándose con status en vivo."""
    import importlib

    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        console.print("[red]Tarea no encontrada[/]")
        return

    console.print()
    console.rule(f"[bold blue]Pipeline: {tarea['titulo']}[/]")
    console.print()

    pasos = [
        ("🎨 Portada", "Generando portada UTM con PIL..."),
        ("📄 HTML", "Convirtiendo contenido a HTML..."),
        ("📑 PDF", "Playwright: HTML → PDF..."),
        ("🔎 Review", "Validando estructura, APA, palabras..."),
        ("📁 Organizar", "Moviendo a carpeta de asignatura..."),
        ("✅ Estado", "Marcando como completada..."),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Pipeline", total=len(pasos))

        for i, (nombre, desc) in enumerate(pasos):
            progress.update(task, description=f"{nombre} — {desc}")
            time.sleep(0.3)  # Visual feedback mínimo
            progress.advance(task)

    console.print()

    # Ejecutar pipeline real
    resultado = gestor.flujo_completo(tarea_id)

    console.print()

    if resultado.get("exito"):
        console.print(Panel(
            "[bold green]Pipeline completado exitosamente[/]\n\n"
            + "\n".join(
                f"  {'✅' if p['estado'] == 'ok' else '❌'} {p['paso'].upper()}"
                for p in resultado.get("pasos", [])
            ),
            title="Resultado",
            border_style="green",
        ))
    else:
        fallas = resultado.get("fallas", [])
        console.print(Panel(
            "[bold red]Pipeline requiere corrección[/]\n\n"
            + "\n".join(f"  ❌ {f['check']}: {f.get('detalle', '')}" for f in fallas),
            title="Resultado",
            border_style="red",
        ))

        # Mostrar instrucciones de agentes para las fallas
        console.print()
        console.rule("[yellow]Instrucciones para agentes[/]")
        for panel in mostrar_agentes(tarea_id):
            console.print(panel)

    return resultado


# ─── PREVIEW COMPLETO ───────────────────────────────────────

def preview_completo(tarea_id):
    """Muestra el dashboard completo de una tarea."""
    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        console.print(f"[red]Tarea #{tarea_id} no encontrada[/]")
        return

    console.print()
    console.rule(f"[bold blue]Preview: Tarea #{tarea_id}[/]")
    console.print()

    # Info básica
    info = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    info.add_column("", style="bold cyan", width=14)
    info.add_column("")
    info.add_row("Título", tarea["titulo"])
    info.add_row("Asignatura", tarea["asignatura"])
    info.add_row("Estado", tarea["estado"])
    info.add_row("Archivo", str(tarea.get("archivo_generado") or "[yellow]No generado[/]"))
    console.print(info)
    console.print()

    # Portada
    console.print(preview_portada(tarea))
    console.print()

    # Contenido
    console.print(preview_contenido(tarea))
    console.print()

    # Review
    console.print(preview_review(tarea_id))
    console.print()

    # Agentes
    console.rule("[bold blue]Panel de Agentes[/]")
    console.print()
    for panel in mostrar_agentes(tarea_id):
        console.print(panel)
        console.print()


# ─── CLI ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        console.print("""[bold blue]Preview Dashboard[/]
  python preview.py <id>              Preview completo
  python preview.py <id> portada      Solo portada
  python preview.py <id> contenido    Solo contenido
  python preview.py <id> review       Solo review
  python preview.py <id> agentes      Solo panel de agentes
  python preview.py pipeline <id>     Pipeline en vivo""")
        return

    if sys.argv[1] == "pipeline":
        if len(sys.argv) < 3:
            console.print("[red]Uso: python preview.py pipeline <id>[/]")
            return
        pipeline_live(int(sys.argv[2]))
        return

    tarea_id = int(sys.argv[1])
    vista = sys.argv[2] if len(sys.argv) > 2 else "completo"

    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        console.print(f"[red]Tarea #{tarea_id} no encontrada[/]")
        return

    if vista == "portada":
        console.print(preview_portada(tarea))
    elif vista == "contenido":
        console.print(preview_contenido(tarea))
    elif vista == "review":
        console.print(preview_review(tarea_id))
    elif vista == "agentes":
        console.rule("[bold blue]Panel de Agentes[/]")
        console.print()
        for panel in mostrar_agentes(tarea_id):
            console.print(panel)
            console.print()
    else:
        preview_completo(tarea_id)


if __name__ == "__main__":
    main()
