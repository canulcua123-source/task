#!/usr/bin/env python3
"""
Organizador de Entregas — Gestión automática de carpetas por asignatura.
Crea estructura de carpetas, mueve archivos y mantiene orden.

Uso:
  python organizar.py setup          # Crea carpetas para todas las asignaturas
  python organizar.py mover          # Mueve archivos sueltos a sus carpetas
  python organizar.py estado         # Muestra estado de organización
  python organizar.py limpiar        # Limpia archivos temporales
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
import gestor


ENTREGAS_DIR = BASE_DIR / "sandbox" / "entregas"


def _cargar_mapeo_carpetas():
    """Deriva nombres de carpeta desde config.json. No hardcodea nada."""
    config = gestor.load_config()
    mapeo = {}
    for asig in config["asignaturas"]:
        # Nombre limpio: quita caracteres problemáticos, acorta
        nombre = asig["nombre"]
        # Abreviar nombres largos comunes
        nombre = nombre.replace("Tecnologías de la Información", "TI")
        nombre = nombre.replace("Inteligencia Artificial", "IA")
        mapeo[asig["clave"]] = nombre
    return mapeo


def obtener_carpeta(clave):
    """Retorna el path de la carpeta para una asignatura (derivado de config)."""
    mapeo = _cargar_mapeo_carpetas()
    nombre = mapeo.get(clave, clave)
    return ENTREGAS_DIR / nombre


def setup_carpetas():
    """Crea carpetas para todas las asignaturas registradas."""
    config = gestor.load_config()
    creadas = []

    for asig in config["asignaturas"]:
        clave = asig["clave"]
        carpeta = obtener_carpeta(clave)
        if not carpeta.exists():
            carpeta.mkdir(parents=True, exist_ok=True)
            creadas.append(str(carpeta))
            print(f"  📁 Creada: {carpeta.name}/")
        else:
            print(f"  ✅ Existe: {carpeta.name}/")

    if creadas:
        print(f"\n{len(creadas)} carpeta(s) creada(s).")
    else:
        print("\nTodas las carpetas ya existen.")
    return creadas


def mover_archivos():
    """Mueve archivos sueltos en entregas/ a la carpeta de su asignatura."""
    movidos = []
    errores = []

    # Primero asegurar que existen las carpetas
    setup_carpetas()
    print()

    for archivo in ENTREGAS_DIR.iterdir():
        if archivo.is_dir():
            continue
        if archivo.name.startswith("~$") or archivo.name.startswith("."):
            continue

        # Detectar asignatura por prefijo del nombre (etica_, bdnube_, ia_)
        nombre = archivo.name.lower()
        mapeo = _cargar_mapeo_carpetas()
        clave_detectada = None
        for clave in mapeo:
            if nombre.startswith(f"{clave}_"):
                clave_detectada = clave
                break

        if not clave_detectada:
            print(f"  ⚠️  No clasificado: {archivo.name}")
            continue

        destino_dir = obtener_carpeta(clave_detectada)
        destino = destino_dir / archivo.name

        if destino.exists():
            print(f"  ⏭️  Ya existe en destino: {archivo.name}")
            continue

        shutil.move(str(archivo), str(destino))
        movidos.append({"archivo": archivo.name, "destino": str(destino_dir.name)})
        print(f"  📦 {archivo.name} → {destino_dir.name}/")

        # Actualizar ruta en tareas_db
        _actualizar_ruta_db(str(archivo), str(destino))

    if movidos:
        print(f"\n{len(movidos)} archivo(s) movido(s).")
    else:
        print("\nNo hay archivos para mover.")
    return movidos


def _actualizar_ruta_db(ruta_vieja, ruta_nueva):
    """Actualiza la ruta del archivo generado en la DB."""
    db = gestor.load_db()
    for t in db["tareas"]:
        if t.get("archivo_generado") and Path(t["archivo_generado"]).name == Path(ruta_vieja).name:
            t["archivo_generado"] = ruta_nueva
            gestor.save_db(db)
            return True
    return False


def estado():
    """Muestra el estado de organización de las entregas."""
    config = gestor.load_config()
    db = gestor.load_db()

    print(f"\n{'═' * 55}")
    print(f"  ESTADO DE ENTREGAS")
    print(f"{'═' * 55}")

    for asig in config["asignaturas"]:
        clave = asig["clave"]
        carpeta = obtener_carpeta(clave)
        tareas = [t for t in db["tareas"] if t["asignatura_clave"] == clave]
        completadas = [t for t in tareas if t["estado"] in ("completada", "entregada")]

        if carpeta.exists():
            archivos = [f for f in carpeta.iterdir() if f.is_file() and not f.name.startswith(".")]
            n_archivos = len(archivos)
        else:
            n_archivos = 0

        print(f"\n  📚 {asig['nombre']}")
        print(f"     Carpeta: {'✅' if carpeta.exists() else '❌'} {carpeta.name}/")
        print(f"     Tareas: {len(tareas)} total, {len(completadas)} completadas")
        print(f"     Archivos: {n_archivos}")

        if carpeta.exists():
            for f in sorted(carpeta.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    size_kb = os.path.getsize(f) / 1024
                    print(f"       📄 {f.name} ({size_kb:.0f} KB)")

    # Archivos sin clasificar
    sueltos = [
        f for f in ENTREGAS_DIR.iterdir()
        if f.is_file() and not f.name.startswith("~$") and not f.name.startswith(".")
    ]
    if sueltos:
        print(f"\n  ⚠️  Archivos sin clasificar en entregas/:")
        for f in sueltos:
            print(f"       {f.name}")

    print(f"\n{'═' * 55}\n")


def estado_json():
    """Versión JSON del estado para parsing agéntico."""
    config = gestor.load_config()
    db = gestor.load_db()
    resultado = {}

    for asig in config["asignaturas"]:
        clave = asig["clave"]
        carpeta = obtener_carpeta(clave)
        tareas = [t for t in db["tareas"] if t["asignatura_clave"] == clave]
        archivos = []
        if carpeta.exists():
            archivos = [
                {"nombre": f.name, "size_kb": round(os.path.getsize(f) / 1024)}
                for f in sorted(carpeta.iterdir())
                if f.is_file() and not f.name.startswith(".")
            ]
        resultado[clave] = {
            "asignatura": asig["nombre"],
            "carpeta": str(carpeta),
            "existe": carpeta.exists(),
            "tareas_total": len(tareas),
            "tareas_completadas": len([t for t in tareas if t["estado"] in ("completada", "entregada")]),
            "archivos": archivos,
        }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return resultado


def limpiar():
    """Elimina archivos temporales (~$, .tmp)."""
    eliminados = 0
    for f in ENTREGAS_DIR.rglob("*"):
        if f.is_file() and (f.name.startswith("~$") or f.suffix == ".tmp"):
            f.unlink()
            eliminados += 1
            print(f"  🗑️  {f.name}")

    print(f"\n{eliminados} archivo(s) temporal(es) eliminados." if eliminados else "\nNo hay archivos temporales.")


# ─── CLI ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python organizar.py [setup|mover|estado|limpiar]")
        return

    cmd = sys.argv[1]
    if cmd == "setup":
        setup_carpetas()
    elif cmd == "mover":
        mover_archivos()
    elif cmd == "estado":
        if "--json" in sys.argv:
            estado_json()
        else:
            estado()
    elif cmd == "limpiar":
        limpiar()
    else:
        print(f"Comando desconocido: {cmd}")


if __name__ == "__main__":
    main()
