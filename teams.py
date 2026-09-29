#!/usr/bin/env python3
"""
Integración con Microsoft Teams Education.
Permite ver tareas asignadas, descargar detalles y subir entregas.
"""

import json
import os
import stat
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

import msal
import requests

BASE_DIR = Path(__file__).parent
TOKEN_CACHE = BASE_DIR / ".token_cache.json"
CONFIG_PATH = BASE_DIR / "config.json"

# Microsoft Graph — usamos el client_id público de Microsoft para device code flow
# Este es el client_id genérico para apps CLI de Microsoft (no necesita registro)
CLIENT_ID = "1b730954-1685-4b74-9bfd-dac224a7b894"  # Microsoft Graph PowerShell public client
AUTHORITY = "https://login.microsoftonline.com/organizations"
SCOPES = [
    "https://graph.microsoft.com/EduAssignments.Read",
    "https://graph.microsoft.com/EduAssignments.ReadWrite",
    "https://graph.microsoft.com/Files.ReadWrite",
    "https://graph.microsoft.com/User.Read",
]
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def _get_cache():
    """Carga o crea cache de tokens MSAL."""
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE.exists():
        cache.deserialize(TOKEN_CACHE.read_text())
    return cache


def _save_cache(cache):
    """Guarda cache de tokens con permisos restrictivos (600)."""
    if cache.has_state_changed:
        TOKEN_CACHE.write_text(cache.serialize())
        TOKEN_CACHE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600


def _get_app(cache):
    """Crea la app MSAL."""
    return msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )


def obtener_token():
    """Obtiene un token de acceso, usando cache o device code flow."""
    cache = _get_cache()
    app = _get_app(cache)

    # Intentar obtener token desde cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            _save_cache(cache)
            return result["access_token"]

    # Device code flow — el usuario debe autenticarse
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"Error al iniciar autenticación: {flow.get('error_description', 'desconocido')}")
        return None

    print("\n" + "=" * 60)
    print("AUTENTICACIÓN CON MICROSOFT TEAMS")
    print("=" * 60)
    print(f"\n1. Abre: {flow['verification_uri']}")
    print(f"2. Ingresa el código: {flow['user_code']}")
    print(f"3. Inicia sesión con tu cuenta escolar de la UTM")
    print("\nEsperando autenticación...\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        _save_cache(cache)
        print("Autenticación exitosa!")
        return result["access_token"]
    else:
        print(f"Error: {result.get('error_description', 'No se pudo autenticar')}")
        return None


def _graph_get(endpoint, token):
    """Hace un GET al Graph API."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{GRAPH_URL}{endpoint}", headers=headers, timeout=30)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 401:
        print("Token expirado. Vuelve a autenticarte.")
        return None
    else:
        print(f"Error {r.status_code}: {r.text[:200]}")
        return None


def _graph_post(endpoint, token, data=None, files=None, headers_extra=None):
    """Hace un POST al Graph API."""
    headers = {"Authorization": f"Bearer {token}"}
    if headers_extra:
        headers.update(headers_extra)
    if files:
        r = requests.post(f"{GRAPH_URL}{endpoint}", headers=headers, files=files, timeout=30)
    else:
        headers["Content-Type"] = "application/json"
        r = requests.post(f"{GRAPH_URL}{endpoint}", headers=headers, json=data, timeout=30)
    return r


def _graph_put(url, token, data, content_type="application/octet-stream"):
    """Hace un PUT (para subir archivos)."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
    }
    r = requests.put(url, headers=headers, data=data, timeout=30)
    return r


# ─── Funciones principales ─────────────────────────────────────

def mi_perfil(token):
    """Muestra info del usuario autenticado."""
    data = _graph_get("/me", token)
    if data:
        print(f"Usuario: {data.get('displayName', '?')}")
        print(f"Email: {data.get('mail', data.get('userPrincipalName', '?'))}")
    return data


def listar_clases(token):
    """Lista las clases del estudiante en Teams."""
    data = _graph_get("/education/me/classes", token)
    if not data or "value" not in data:
        print("No se pudieron obtener las clases.")
        return []

    clases = data["value"]
    if not clases:
        print("No tienes clases registradas en Teams.")
        return []

    print(f"\nClases encontradas: {len(clases)}")
    print(f"{'#':<4} {'Clase':<50} {'ID'}")
    print("─" * 80)
    for i, c in enumerate(clases, 1):
        nombre = c.get("displayName", "Sin nombre")[:48]
        print(f"{i:<4} {nombre:<50} {c['id'][:20]}...")

    return clases


def listar_tareas_teams(token, class_id=None):
    """Lista las tareas asignadas. Si no se da class_id, lista de todas las clases."""
    todas = []

    if class_id:
        data = _graph_get(f"/education/classes/{class_id}/assignments", token)
        if data and "value" in data:
            todas.extend(data["value"])
    else:
        # Obtener de todas las clases
        clases = _graph_get("/education/me/classes", token)
        if clases and "value" in clases:
            for c in clases["value"]:
                data = _graph_get(f"/education/classes/{c['id']}/assignments", token)
                if data and "value" in data:
                    for a in data["value"]:
                        a["_clase"] = c.get("displayName", "?")
                    todas.extend(data["value"])

    if not todas:
        print("No se encontraron tareas.")
        return []

    # Ordenar por fecha de entrega
    todas.sort(key=lambda x: (x.get("dueDateTime") or {}).get("dateTime", "9999"))

    print(f"\nTareas encontradas: {len(todas)}")
    print(f"{'#':<4} {'Estado':<12} {'Clase':<25} {'Tarea':<35} {'Entrega'}")
    print("─" * 100)
    for i, t in enumerate(todas, 1):
        estado = t.get("status", "?")
        clase = t.get("_clase", "")[:23]
        nombre = t.get("displayName", "Sin nombre")[:33]
        due = t.get("dueDateTime", {}).get("dateTime", "Sin fecha")
        if due != "Sin fecha":
            try:
                due = datetime.fromisoformat(due.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                pass
        icon = {"assigned": "📋", "draft": "📝"}.get(estado, "?")
        print(f"{i:<4} {icon} {estado:<10} {clase:<25} {nombre:<35} {due}")

    return todas


def ver_tarea_detalle(token, class_id, assignment_id):
    """Obtiene el detalle de una tarea específica."""
    data = _graph_get(f"/education/classes/{class_id}/assignments/{assignment_id}", token)
    if not data:
        return None

    print(f"\n{'=' * 60}")
    print(f"Tarea: {data.get('displayName', '?')}")
    print(f"{'=' * 60}")
    print(f"Estado: {data.get('status', '?')}")

    # Instrucciones
    instrucciones = data.get("instructions", {})
    if instrucciones:
        content = instrucciones.get("content", "Sin instrucciones")
        # Limpiar HTML básico
        import re
        content = re.sub(r'<[^>]+>', '', content)
        print(f"Instrucciones:\n{content}")

    # Fecha
    due = data.get("dueDateTime", {}).get("dateTime", "Sin fecha")
    if due != "Sin fecha":
        try:
            due = datetime.fromisoformat(due.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            pass
    print(f"Fecha de entrega: {due}")

    # Recursos adjuntos
    resources = _graph_get(
        f"/education/classes/{class_id}/assignments/{assignment_id}/resources", token
    )
    if resources and resources.get("value"):
        print(f"\nRecursos adjuntos: {len(resources['value'])}")
        for r in resources["value"]:
            res = r.get("resource", {})
            print(f"  - {res.get('displayName', '?')} ({res.get('@odata.type', '?')})")

    return data


def obtener_mi_submission(token, class_id, assignment_id):
    """Obtiene la submission del estudiante para una tarea."""
    data = _graph_get(
        f"/education/classes/{class_id}/assignments/{assignment_id}/submissions", token
    )
    if data and "value" in data and data["value"]:
        return data["value"][0]  # Primera submission (la del estudiante)
    return None


def subir_archivo_tarea(token, class_id, assignment_id, archivo_path):
    """Sube un archivo como entrega de una tarea."""
    archivo = Path(archivo_path)
    if not archivo.exists():
        print(f"Archivo no encontrado: {archivo_path}")
        return False

    # Obtener submission
    submission = obtener_mi_submission(token, class_id, assignment_id)
    if not submission:
        print("No se encontró tu submission para esta tarea.")
        return False

    submission_id = submission["id"]

    # Crear carpeta de recursos y subir archivo
    # Paso 1: Crear upload session
    setup_url = f"/education/classes/{class_id}/assignments/{assignment_id}/submissions/{submission_id}/resources"

    # Paso 1: setupResourcesFolder (debe ser POST, no GET)
    setup_resp = _graph_post(
        f"/education/classes/{class_id}/assignments/{assignment_id}/submissions/{submission_id}/setUpResourcesFolder",
        token,
        data={}
    )

    if not setup_resp or setup_resp.status_code not in (200, 201):
        status = setup_resp.status_code if setup_resp else "sin respuesta"
        print(f"Error al preparar carpeta de recursos: {status}")
        return False

    setup_data = setup_resp.json()

    # Paso 2: Extraer drive info desde resourcesFolderUrl
    resources_folder_url = setup_data.get("resourcesFolderUrl", "")
    if not resources_folder_url:
        print("No se obtuvo resourcesFolderUrl.")
        return False

    # Paso 3: Subir archivo al folder via resourcesFolderUrl
    file_name = archivo.name
    file_name_encoded = quote(file_name)
    with open(archivo, "rb") as f:
        file_data = f.read()

    upload_url = f"{resources_folder_url}:/{file_name_encoded}:/content"
    r = _graph_put(upload_url, token, file_data)

    if r.status_code not in (200, 201):
        print(f"Error al subir archivo: {r.status_code} {r.text[:200]}")
        return False

    uploaded = r.json()
    print(f"Archivo subido: {file_name}")

    # Paso 4: Agregar como recurso usando URL Graph del item (no webUrl)
    drive_id = uploaded.get("parentReference", {}).get("driveId", "")
    item_id = uploaded.get("id", "")
    if not drive_id or not item_id:
        print("Error: No se pudo obtener driveId/itemId del archivo subido.")
        return False
    file_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"

    resource_data = {
        "resource": {
            "@odata.type": "#microsoft.graph.educationFileResource",
            "displayName": file_name,
            "fileUrl": file_url,
        }
    }
    r2 = _graph_post(setup_url, token, data=resource_data)
    if r2.status_code in (200, 201):
        print("Recurso agregado a la entrega.")
        return True
    else:
        print(f"Error al agregar recurso: {r2.status_code} {r2.text[:200]}")
        return False


def entregar_tarea(token, class_id, assignment_id):
    """Envía/entrega la tarea (submit)."""
    submission = obtener_mi_submission(token, class_id, assignment_id)
    if not submission:
        print("No se encontró tu submission.")
        return False

    submission_id = submission["id"]
    r = _graph_post(
        f"/education/classes/{class_id}/assignments/{assignment_id}/submissions/{submission_id}/submit",
        token
    )
    if r.status_code in (200, 201):
        print("Tarea entregada exitosamente!")
        return True
    else:
        print(f"Error al entregar: {r.status_code} {r.text[:200]}")
        return False


# ─── Función para uso agéntico (Claude) ───────────────────────

def revisar_tareas_pendientes():
    """Revisa todas las tareas pendientes en Teams. Para uso agéntico."""
    token = obtener_token()
    if not token:
        return None

    clases = _graph_get("/education/me/classes", token)
    if not clases or "value" not in clases:
        return {"error": "No se pudieron obtener clases"}

    resultado = {
        "usuario": None,
        "clases": [],
        "tareas_pendientes": [],
    }

    # Info usuario
    user = _graph_get("/me", token)
    if user:
        resultado["usuario"] = user.get("displayName", "?")

    for c in clases["value"]:
        clase_info = {"nombre": c.get("displayName", "?"), "id": c["id"]}
        resultado["clases"].append(clase_info)

        assignments = _graph_get(f"/education/classes/{c['id']}/assignments", token)
        if assignments and "value" in assignments:
            for a in assignments["value"]:
                if a.get("status") == "assigned":
                    due = a.get("dueDateTime", {}).get("dateTime", None)
                    fecha_str = None
                    if due:
                        try:
                            fecha_str = datetime.fromisoformat(
                                due.replace("Z", "+00:00")
                            ).strftime("%Y-%m-%d %H:%M")
                        except (ValueError, TypeError):
                            fecha_str = due

                    # Ver si ya fue entregada
                    submission = obtener_mi_submission(token, c["id"], a["id"])
                    sub_status = submission.get("status", "?") if submission else "?"

                    resultado["tareas_pendientes"].append({
                        "class_id": c["id"],
                        "assignment_id": a["id"],
                        "clase": c.get("displayName", "?"),
                        "nombre": a.get("displayName", "?"),
                        "instrucciones": (a.get("instructions", {}) or {}).get("content", ""),
                        "fecha_entrega": fecha_str,
                        "estado_submission": sub_status,
                    })

    return resultado


def obtener_tareas_estructuradas():
    """
    Retorna lista de dicts lista para importar vía gestor.importar_desde_teams().
    Cada dict contiene: class_name, class_id, assignment_id, title, description,
    dueDateTime, status, instructions.
    """
    import re

    token = obtener_token()
    if not token:
        return []

    clases = _graph_get("/education/me/classes", token)
    if not clases or "value" not in clases:
        return []

    resultado = []
    for c in clases["value"]:
        class_id = c["id"]
        class_name = c.get("displayName", "?")

        assignments = _graph_get(f"/education/classes/{class_id}/assignments", token)
        if not assignments or "value" not in assignments:
            continue

        for a in assignments["value"]:
            due_raw = (a.get("dueDateTime") or {}).get("dateTime", None)
            instructions_html = (a.get("instructions") or {}).get("content", "") or ""
            instructions_text = re.sub(r'<[^>]+>', '', instructions_html).strip()

            resultado.append({
                "class_name": class_name,
                "class_id": class_id,
                "assignment_id": a["id"],
                "title": a.get("displayName", "Sin nombre"),
                "description": instructions_text,
                "dueDateTime": due_raw,
                "status": a.get("status", "?"),
                "instructions": instructions_text,
            })

    return resultado


# ─── CLI ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("""
Teams Integration — Gestor de Tareas UTM
Uso:
  python teams.py login          — Autenticarte con tu cuenta escolar
  python teams.py perfil         — Ver tu perfil
  python teams.py clases         — Listar tus clases
  python teams.py tareas         — Ver todas las tareas
  python teams.py detalle <#>    — Ver detalle de una tarea (necesita listar primero)
  python teams.py subir <class_id> <assignment_id> <archivo>
  python teams.py entregar <class_id> <assignment_id>
  python teams.py revisar        — Resumen de tareas pendientes (para Claude)
        """)
        return

    cmd = sys.argv[1]

    if cmd == "login":
        token = obtener_token()
        if token:
            mi_perfil(token)

    elif cmd == "perfil":
        token = obtener_token()
        if token:
            mi_perfil(token)

    elif cmd == "clases":
        token = obtener_token()
        if token:
            listar_clases(token)

    elif cmd == "tareas":
        token = obtener_token()
        if token:
            listar_tareas_teams(token)

    elif cmd == "revisar":
        resultado = revisar_tareas_pendientes()
        if resultado:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))

    elif cmd == "subir":
        if len(sys.argv) < 5:
            print("Uso: python teams.py subir <class_id> <assignment_id> <archivo>")
            return
        token = obtener_token()
        if token:
            subir_archivo_tarea(token, sys.argv[2], sys.argv[3], sys.argv[4])

    elif cmd == "entregar":
        if len(sys.argv) < 4:
            print("Uso: python teams.py entregar <class_id> <assignment_id>")
            return
        token = obtener_token()
        if token:
            entregar_tarea(token, sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
