#!/usr/bin/env python3
"""
Pipeline rápido: tarea_id → PDF completo con portada UTM.
Usa Playwright (HTML→PDF). NO usa docx2pdf.
Tiempo objetivo: <30 segundos.

Uso:
  python generar_pdf.py <tarea_id>
  python generar_pdf.py <tarea_id> --abrir    # abre el PDF al terminar
"""

import base64
import html as html_mod
import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

import gestor


# ─── 1. PORTADA ──────────────────────────────────────────────

def generar_portada_b64(tarea):
    """Genera la portada UTM como PNG y devuelve base64."""
    config = gestor.load_config()
    portada_path = gestor._crear_portada_imagen(config, tarea)
    with open(portada_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    Path(portada_path).unlink()
    return b64


# ─── 2. CONTENIDO → HTML ────────────────────────────────────

def contenido_a_html(contenido):
    """Convierte el array de secciones a HTML."""
    if not isinstance(contenido, list):
        return f"<p>{html_mod.escape(str(contenido))}</p>"

    parts = []
    for sec in contenido:
        tipo = sec.get("tipo", "parrafo")
        if tipo == "titulo":
            parts.append(f'<h1>{html_mod.escape(sec["texto"])}</h1>')
        elif tipo == "subtitulo":
            parts.append(f'<h2>{html_mod.escape(sec["texto"])}</h2>')
        elif tipo == "parrafo":
            parts.append(f'<p>{html_mod.escape(sec["texto"])}</p>')
        elif tipo == "lista":
            items = "".join(f"<li>{html_mod.escape(it)}</li>" for it in sec.get("items", []))
            parts.append(f"<ul class='lista'>{items}</ul>")
    return "\n".join(parts)


# ─── 3. HTML COMPLETO ───────────────────────────────────────

def construir_html(portada_b64, contenido_html):
    """Arma el HTML final: portada (página 1) + contenido."""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  @page {{ size: Letter; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, sans-serif; color: #333; }}

  .portada {{
    width: 100%; height: 100vh;
    page-break-after: always;
    display: flex; justify-content: center; align-items: center;
    background: white;
  }}
  .portada img {{ width: 100%; height: 100%; object-fit: contain; }}

  .contenido {{ padding: 60px 70px; }}
  h1 {{
    font-size: 18pt; color: #003366; border-bottom: 2px solid #003366;
    padding-bottom: 6px; margin: 30px 0 16px 0;
  }}
  h1:first-child {{ margin-top: 0; }}
  h2 {{ font-size: 14pt; color: #003366; margin: 22px 0 10px 0; }}
  p {{
    font-size: 12pt; line-height: 1.7; text-align: justify;
    margin: 8px 0; text-indent: 1.25cm;
  }}
  ul.lista {{ margin: 8px 0 8px 30px; }}
  ul.lista li {{ font-size: 12pt; line-height: 1.6; margin: 4px 0; }}

  table {{
    width: 100%; border-collapse: collapse; margin: 16px 0 24px 0;
    font-size: 10.5pt;
  }}
  th {{
    background: #003366; color: white; padding: 10px 8px;
    text-align: left; font-weight: bold; border: 1px solid #003366;
  }}
  td {{
    padding: 10px 8px; border: 1px solid #bbb;
    vertical-align: top; line-height: 1.5;
  }}
  tr:nth-child(even) td {{ background: #f5f5f5; }}
</style>
</head><body>

<div class="portada">
  <img src="data:image/png;base64,{portada_b64}" />
</div>

<div class="contenido">
{contenido_html}
</div>

</body></html>"""


# ─── 4. HTML → PDF ──────────────────────────────────────────

def html_a_pdf(html_str, pdf_path):
    """Convierte HTML a PDF con Playwright."""
    from playwright.sync_api import sync_playwright

    html_tmp = "/tmp/_tarea_pdf_tmp.html"
    Path(html_tmp).write_text(html_str, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_tmp}")
        page.wait_for_timeout(1500)
        page.pdf(
            path=str(pdf_path),
            format="Letter",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    Path(html_tmp).unlink(missing_ok=True)


# ─── 5. VALIDACIÓN ──────────────────────────────────────────

def validar_pdf(pdf_path, tarea):
    """Verifica que el PDF existe y tiene tamaño razonable."""
    errores = []
    if not Path(pdf_path).exists():
        errores.append("PDF no se generó")
        return errores

    size_kb = os.path.getsize(pdf_path) / 1024
    if size_kb < 10:
        errores.append(f"PDF muy pequeño ({size_kb:.0f} KB) — probablemente vacío")
    if size_kb > 10000:
        errores.append(f"PDF muy grande ({size_kb:.0f} KB) — revisar imágenes")

    # Verificar contenido tiene secciones mínimas
    contenido = tarea.get("contenido", [])
    if isinstance(contenido, list):
        tipos = [s.get("tipo") for s in contenido]
        if "titulo" not in tipos:
            errores.append("Falta al menos un título en el contenido")
        if "parrafo" not in tipos:
            errores.append("Falta al menos un párrafo en el contenido")

    return errores


# ─── MAIN ───────────────────────────────────────────────────

def generar_pdf_completo(tarea_id, abrir=False):
    """Pipeline completo: tarea_id → PDF."""
    t0 = time.time()

    # Obtener tarea
    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        print(f"Error: Tarea #{tarea_id} no encontrada.")
        return None

    contenido = tarea.get("contenido")
    if not isinstance(contenido, list) or not contenido:
        print(f"Error: Tarea #{tarea_id} no tiene contenido para generar.")
        return None

    print(f"Generando PDF para: {tarea['titulo']}")

    # Paso 1: Portada
    portada_b64 = generar_portada_b64(tarea)
    t1 = time.time()
    print(f"  [1/4] Portada generada ({t1-t0:.1f}s)")

    # Paso 2: Contenido → HTML
    contenido_html = contenido_a_html(contenido)
    t2 = time.time()
    print(f"  [2/4] HTML generado ({t2-t1:.1f}s)")

    # Paso 3: HTML completo → PDF
    html_final = construir_html(portada_b64, contenido_html)

    titulo_safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in tarea["titulo"])[:40]
    nombre = f"{tarea['asignatura_clave']}_{tarea['id']}_{titulo_safe}.pdf"
    pdf_dir = BASE_DIR / "sandbox" / "entregas"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / nombre

    html_a_pdf(html_final, pdf_path)
    t3 = time.time()
    print(f"  [3/4] PDF generado ({t3-t2:.1f}s)")

    # Paso 4: Validación
    errores = validar_pdf(pdf_path, tarea)
    t4 = time.time()
    if errores:
        print(f"  [4/4] ERRORES encontrados:")
        for e in errores:
            print(f"    ✗ {e}")
    else:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"  [4/4] Validación OK ({size_kb:.0f} KB)")

    total = t4 - t0
    print(f"\n  Total: {total:.1f}s — {'OK' if total < 60 else 'LENTO (>1min)'}")
    print(f"  Archivo: {pdf_path}")

    # Actualizar DB
    db = gestor.load_db()
    for t in db["tareas"]:
        if t["id"] == tarea_id:
            t["archivo_generado"] = str(pdf_path)
            break
    gestor.save_db(db)

    if abrir:
        os.system(f'open "{pdf_path}"')

    return str(pdf_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python generar_pdf.py <tarea_id> [--abrir]")
        sys.exit(1)

    tarea_id = int(sys.argv[1])
    abrir = "--abrir" in sys.argv
    generar_pdf_completo(tarea_id, abrir=abrir)
