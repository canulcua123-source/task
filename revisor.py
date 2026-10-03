#!/usr/bin/env python3
"""
Revisor de Calidad — Validador automático de tareas escolares UTM.
Verifica criterios de evaluación: formato, estructura, APA, extensión, etc.

Uso:
  python revisor.py <tarea_id>                    # Revisa una tarea
  python revisor.py <tarea_id> --criterios <json>  # Revisa con criterios custom
  python revisor.py todos                          # Revisa todas las pendientes/en_progreso
"""

import json
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
import gestor


# ─── Criterios de evaluación por defecto ────────────────────
DEFAULT_CRITERIOS = {
    "min_palabras": 300,
    "max_palabras": None,
    "requiere_introduccion": True,
    "requiere_conclusion": True,
    "requiere_referencias": True,
    "fuente_requerida": "Arial",
    "formato_apa": True,
    "requiere_portada": True,
    "secciones_minimas": 3,
}


# ─── Extracción de texto del contenido ──────────────────────

def extraer_texto(contenido):
    """Extrae todo el texto plano del contenido de una tarea."""
    if not isinstance(contenido, list):
        return str(contenido)

    textos = []
    for sec in contenido:
        tipo = sec.get("tipo", "")
        if tipo in ("titulo", "subtitulo", "parrafo"):
            textos.append(sec.get("texto", ""))
        elif tipo == "lista":
            textos.extend(sec.get("items", []))
    return " ".join(textos)


def contar_palabras(contenido):
    """Cuenta las palabras en el contenido (excluyendo títulos de sección)."""
    if not isinstance(contenido, list):
        return len(str(contenido).split())

    palabras = 0
    for sec in contenido:
        tipo = sec.get("tipo", "")
        if tipo == "parrafo":
            palabras += len(sec.get("texto", "").split())
        elif tipo == "lista":
            for item in sec.get("items", []):
                palabras += len(item.split())
    return palabras


def obtener_secciones(contenido):
    """Retorna lista de títulos/subtítulos encontrados."""
    if not isinstance(contenido, list):
        return []
    return [
        sec.get("texto", "").lower()
        for sec in contenido
        if sec.get("tipo") in ("titulo", "subtitulo")
    ]


# ─── Checks individuales ───────────────────────────────────

def check_palabras(contenido, criterios):
    """Verifica conteo de palabras."""
    count = contar_palabras(contenido)
    resultado = {"check": "Conteo de palabras", "valor": f"{count} palabras"}

    min_p = criterios.get("min_palabras")
    max_p = criterios.get("max_palabras")

    if min_p and count < min_p:
        resultado["estado"] = "FALLA"
        resultado["detalle"] = f"Mínimo requerido: {min_p}. Faltan ~{min_p - count} palabras."
    elif max_p and count > max_p:
        resultado["estado"] = "ADVERTENCIA"
        resultado["detalle"] = f"Máximo recomendado: {max_p}. Excede por ~{count - max_p} palabras."
    else:
        resultado["estado"] = "OK"
        rango = f"{min_p or '?'}-{max_p or '∞'}"
        resultado["detalle"] = f"Dentro del rango ({rango})"

    return resultado


def check_estructura(contenido, criterios):
    """Verifica estructura del documento (intro, conclusión, secciones)."""
    secciones = obtener_secciones(contenido)
    resultados = []

    # Introducción
    if criterios.get("requiere_introduccion"):
        tiene_intro = any(
            "introduc" in s for s in secciones
        )
        resultados.append({
            "check": "Introducción",
            "estado": "OK" if tiene_intro else "FALLA",
            "detalle": "Encontrada" if tiene_intro else "No se encontró sección de introducción",
        })

    # Conclusión
    if criterios.get("requiere_conclusion"):
        tiene_conclusion = any(
            "conclusi" in s or "conclus" in s for s in secciones
        )
        resultados.append({
            "check": "Conclusión",
            "estado": "OK" if tiene_conclusion else "FALLA",
            "detalle": "Encontrada" if tiene_conclusion else "No se encontró sección de conclusión",
        })

    # Referencias
    if criterios.get("requiere_referencias"):
        tiene_refs = any(
            "referencia" in s or "bibliograf" in s or "fuentes" in s
            for s in secciones
        )
        # También verificar que haya items en la lista de referencias
        tiene_items_ref = False
        if isinstance(contenido, list):
            for i, sec in enumerate(contenido):
                if sec.get("tipo") in ("titulo", "subtitulo"):
                    texto = sec.get("texto", "").lower()
                    if "referencia" in texto or "bibliograf" in texto:
                        # Buscar lista siguiente
                        if i + 1 < len(contenido) and contenido[i + 1].get("tipo") == "lista":
                            items = contenido[i + 1].get("items", [])
                            tiene_items_ref = len(items) >= 2

        if tiene_refs and tiene_items_ref:
            estado = "OK"
            detalle = "Sección de referencias con fuentes"
        elif tiene_refs:
            estado = "ADVERTENCIA"
            detalle = "Sección encontrada pero pocas fuentes listadas"
        else:
            estado = "FALLA"
            detalle = "No se encontró sección de referencias"

        resultados.append({
            "check": "Referencias",
            "estado": estado,
            "detalle": detalle,
        })

    # Número mínimo de secciones
    min_secciones = criterios.get("secciones_minimas", 3)
    n_titulos = sum(
        1 for sec in (contenido if isinstance(contenido, list) else [])
        if sec.get("tipo") == "titulo"
    )
    resultados.append({
        "check": "Secciones principales",
        "estado": "OK" if n_titulos >= min_secciones else "ADVERTENCIA",
        "valor": f"{n_titulos} títulos principales",
        "detalle": f"Mínimo recomendado: {min_secciones}",
    })

    return resultados


def check_formato_apa(contenido):
    """Verifica indicios de formato APA en referencias."""
    if not isinstance(contenido, list):
        return {"check": "Formato APA", "estado": "N/A", "detalle": "Sin contenido estructurado"}

    # Buscar la sección de referencias
    refs_items = []
    for i, sec in enumerate(contenido):
        if sec.get("tipo") in ("titulo", "subtitulo"):
            texto = sec.get("texto", "").lower()
            if "referencia" in texto or "bibliograf" in texto:
                if i + 1 < len(contenido) and contenido[i + 1].get("tipo") == "lista":
                    refs_items = contenido[i + 1].get("items", [])

    if not refs_items:
        return {"check": "Formato APA", "estado": "ADVERTENCIA", "detalle": "No se encontraron referencias para evaluar"}

    # Heurísticas APA: autor (año), puntos, paréntesis
    apa_score = 0
    for ref in refs_items:
        if re.search(r"\(\d{4}\)", ref):  # (2021)
            apa_score += 1
        if "." in ref and len(ref) > 30:
            apa_score += 0.5

    ratio = apa_score / len(refs_items) if refs_items else 0

    if ratio >= 1.0:
        return {"check": "Formato APA", "estado": "OK", "detalle": f"{len(refs_items)} referencias con formato APA detectado"}
    elif ratio >= 0.5:
        return {"check": "Formato APA", "estado": "ADVERTENCIA", "detalle": f"Algunas referencias no siguen formato APA (autor, año)"}
    else:
        return {"check": "Formato APA", "estado": "FALLA", "detalle": "Referencias no parecen seguir formato APA 7"}


def check_archivo_generado(tarea):
    """Verifica que el archivo generado exista y tenga tamaño razonable."""
    ruta = tarea.get("archivo_generado")
    if not ruta:
        return {"check": "Archivo generado", "estado": "FALLA", "detalle": "No se ha generado archivo"}

    path = Path(ruta)
    if not path.exists():
        return {"check": "Archivo generado", "estado": "FALLA", "detalle": f"Archivo no encontrado: {ruta}"}

    size_kb = os.path.getsize(ruta) / 1024
    ext = path.suffix.lower()

    if size_kb < 5:
        estado = "FALLA"
        detalle = f"Archivo muy pequeño ({size_kb:.0f} KB), probablemente vacío"
    elif ext == ".pdf" and size_kb < 50:
        estado = "ADVERTENCIA"
        detalle = f"PDF pequeño ({size_kb:.0f} KB), verificar contenido"
    else:
        estado = "OK"
        detalle = f"{ext.upper()} — {size_kb:.0f} KB"

    return {"check": "Archivo generado", "estado": estado, "detalle": detalle}


def check_contenido_vacio(contenido):
    """Verifica que el contenido no tenga secciones vacías o muy cortas."""
    if not isinstance(contenido, list):
        return []

    problemas = []
    for i, sec in enumerate(contenido):
        tipo = sec.get("tipo", "")
        if tipo == "parrafo":
            texto = sec.get("texto", "")
            palabras = len(texto.split())
            if palabras < 10:
                problemas.append({
                    "check": f"Párrafo #{i+1} muy corto",
                    "estado": "ADVERTENCIA",
                    "detalle": f"Solo {palabras} palabras: '{texto[:50]}...'" if len(texto) > 50 else f"Solo {palabras} palabras: '{texto}'"
                })
        elif tipo == "lista":
            items = sec.get("items", [])
            if len(items) < 2:
                problemas.append({
                    "check": f"Lista #{i+1} con pocos elementos",
                    "estado": "ADVERTENCIA",
                    "detalle": f"Solo {len(items)} elemento(s)"
                })

    return problemas


# ─── Revisión completa ──────────────────────────────────────

def revisar_tarea(tarea_id, criterios=None):
    """Ejecuta todos los checks sobre una tarea y retorna reporte."""
    tarea = gestor.obtener_tarea(tarea_id)
    if not tarea:
        return {"error": f"Tarea #{tarea_id} no encontrada"}

    criterios = {**DEFAULT_CRITERIOS, **(criterios or {})}
    contenido = tarea.get("contenido", [])
    resultados = []

    # 1. Conteo de palabras
    resultados.append(check_palabras(contenido, criterios))

    # 2. Estructura
    resultados.extend(check_estructura(contenido, criterios))

    # 3. Formato APA
    if criterios.get("formato_apa"):
        resultados.append(check_formato_apa(contenido))

    # 4. Archivo generado
    resultados.append(check_archivo_generado(tarea))

    # 5. Contenido vacío
    resultados.extend(check_contenido_vacio(contenido))

    # Resumen
    fallas = sum(1 for r in resultados if r.get("estado") == "FALLA")
    advertencias = sum(1 for r in resultados if r.get("estado") == "ADVERTENCIA")
    ok = sum(1 for r in resultados if r.get("estado") == "OK")

    veredicto = "APROBADO" if fallas == 0 else "REQUIERE CORRECCIÓN"

    return {
        "tarea_id": tarea_id,
        "titulo": tarea["titulo"],
        "asignatura": tarea["asignatura"],
        "veredicto": veredicto,
        "resumen": {"ok": ok, "advertencias": advertencias, "fallas": fallas},
        "checks": resultados,
        "palabras": contar_palabras(contenido),
    }


def imprimir_reporte(reporte):
    """Imprime el reporte de revisión en formato legible."""
    if "error" in reporte:
        print(f"Error: {reporte['error']}")
        return

    iconos = {"OK": "✅", "FALLA": "❌", "ADVERTENCIA": "⚠️", "N/A": "➖"}

    print(f"\n{'═' * 60}")
    print(f"  REVISIÓN: {reporte['titulo']}")
    print(f"  Asignatura: {reporte['asignatura']}")
    print(f"  Palabras: {reporte['palabras']}")
    print(f"{'═' * 60}")

    for check in reporte["checks"]:
        icono = iconos.get(check["estado"], "?")
        valor = f" ({check['valor']})" if check.get("valor") else ""
        print(f"  {icono} {check['check']}{valor}")
        if check.get("detalle"):
            print(f"     → {check['detalle']}")

    r = reporte["resumen"]
    print(f"\n{'─' * 60}")
    veredicto_icon = "🟢" if reporte["veredicto"] == "APROBADO" else "🔴"
    print(f"  {veredicto_icon} Veredicto: {reporte['veredicto']}")
    print(f"  ✅ {r['ok']} OK  |  ⚠️ {r['advertencias']} Advertencias  |  ❌ {r['fallas']} Fallas")
    print(f"{'═' * 60}\n")


# ─── CLI ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python revisor.py <tarea_id> [--criterios '{...}']")
        print("      python revisor.py todos")
        return

    if sys.argv[1] == "todos":
        db = gestor.load_db()
        for t in db["tareas"]:
            if t["estado"] in ("pendiente", "en_progreso") and isinstance(t.get("contenido"), list) and t["contenido"]:
                reporte = revisar_tarea(t["id"])
                imprimir_reporte(reporte)
        return

    tarea_id = int(sys.argv[1])

    criterios = None
    if "--criterios" in sys.argv:
        idx = sys.argv.index("--criterios")
        if idx + 1 < len(sys.argv):
            criterios = json.loads(sys.argv[idx + 1])

    reporte = revisar_tarea(tarea_id, criterios)

    if "--json" in sys.argv:
        print(json.dumps(reporte, ensure_ascii=False, indent=2))
    else:
        imprimir_reporte(reporte)

    # Exit code para integración con CI/agentes
    if reporte.get("veredicto") == "REQUIERE CORRECCIÓN":
        sys.exit(1)


if __name__ == "__main__":
    main()
