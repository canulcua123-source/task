#!/usr/bin/env python3
"""
Integración con Microsoft Teams vía navegador (Playwright).
Abre Teams web, navega a tareas y las extrae.
"""

import getpass
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / ".teams_session"
os.makedirs(str(SESSION_DIR), mode=0o700, exist_ok=True)
os.chmod(str(SESSION_DIR), 0o700)
TAREAS_TEAMS_PATH = BASE_DIR / "tareas_teams.json"

TEAMS_ASSIGNMENTS_URL = "https://teams.microsoft.com/v2/assignments"
TEAMS_URL = "https://teams.microsoft.com"


def _esperar_teams_cargado(page, timeout=120):
    """Espera hasta que Teams esté completamente cargado (no en login)."""
    print("Esperando que Teams cargue...")
    for i in range(timeout):
        url = page.url
        # Debe estar en teams.microsoft.com sin estar en flujo de login
        if "teams.microsoft.com" in url:
            # No estar en páginas de auth
            if not any(x in url for x in ["login", "oauth", "microsoftonline", "common/oauth"]):
                try:
                    # Buscar elementos que solo existen cuando estás logueado dentro de Teams
                    page.wait_for_selector('[data-tid="app-bar"], [class*="left-rail"], [aria-label*="Teams"], [class*="appBar"]', timeout=3000)
                    print("Teams cargado!")
                    return True
                except Exception:
                    pass
        time.sleep(2)
    print("Timeout esperando Teams.")
    return False


def login(email=None, password=None):
    """Abre Teams y hace login automático si se proporcionan credenciales."""
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel=None,
            viewport={"width": 1280, "height": 900},
            locale="es-MX",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(TEAMS_URL)
        time.sleep(3)

        # Si hay credenciales, automatizar login
        if email and password:
            try:
                # Paso 1: Email
                print("Ingresando correo...")
                email_input = page.wait_for_selector('input[type="email"], input[name="loginfmt"]', timeout=15000)
                if email_input:
                    email_input.fill(email)
                    time.sleep(1)
                    # Click Siguiente
                    page.click('input[type="submit"], button:has-text("Siguiente"), button:has-text("Next")')
                    time.sleep(4)

                # Paso 2: Password (puede redirigir a página de la UTM)
                print("Ingresando contraseña...")
                pwd_input = page.wait_for_selector('input[type="password"], input[name="passwd"], input[name="Password"]', timeout=15000)
                if pwd_input:
                    pwd_input.fill(password)
                    time.sleep(1)
                    # Click Iniciar sesión / Sign in
                    submit_btns = page.query_selector_all('input[type="submit"], button[type="submit"], button:has-text("Iniciar"), button:has-text("Sign in"), button:has-text("Aceptar")')
                    if submit_btns:
                        submit_btns[0].click()
                    time.sleep(5)

                # Paso 3: "Mantener sesión" — click en Sí
                try:
                    stay_btn = page.wait_for_selector('input[value="Yes"], input[value="Sí"], button:has-text("Sí"), button:has-text("Yes")', timeout=10000)
                    if stay_btn:
                        stay_btn.click()
                        print("Sesión mantenida.")
                        time.sleep(3)
                except Exception:
                    pass

            except Exception as e:
                print(f"Error en login automático: {e}")
                print("Intentando esperar login manual...")

        # Esperar a que Teams cargue completamente
        if _esperar_teams_cargado(page, timeout=120):
            time.sleep(5)
            screenshot = BASE_DIR / "assets" / "teams_logged.png"
            page.screenshot(path=str(screenshot))
            print(f"Screenshot: {screenshot}")
            print("Login exitoso! Sesión guardada.")
        else:
            # Guardar screenshot de diagnóstico
            screenshot = BASE_DIR / "assets" / "teams_login_fail.png"
            page.screenshot(path=str(screenshot))
            print(f"Screenshot diagnóstico: {screenshot}")
            print("No se pudo confirmar el login.")

        browser.close()


def revisar_tareas(headless=True):
    """Abre Teams, navega a Tareas y extrae la lista."""
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=headless,
            channel=None,
            viewport={"width": 1280, "height": 900},
            locale="es-MX",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        print("Abriendo Teams...")
        page.goto(TEAMS_URL)

        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        time.sleep(5)

        # Click en "Tareas" del menú lateral
        print("Navegando a Tareas...")
        tareas_btn = page.query_selector('button:has-text("Tareas"), a:has-text("Tareas"), [aria-label*="Tareas"], [data-tid*="assignment"]')
        if tareas_btn:
            tareas_btn.click()
            time.sleep(5)
        else:
            # Intentar ir directo por URL
            page.goto(TEAMS_ASSIGNMENTS_URL)
            time.sleep(8)

        # Screenshot
        screenshot_path = BASE_DIR / "assets" / "teams_tareas.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Screenshot: {screenshot_path}")

        # Extraer tareas del DOM
        tareas = page.evaluate("""
        () => {
            const tareas = [];
            const selectors = [
                '[data-tid="assignment-card"]',
                '.assignment-card',
                '[class*="assignment"]',
                '[class*="Assignment"]',
                '[data-testid*="assignment"]',
                '[role="listitem"]',
            ];

            for (const sel of selectors) {
                const elements = document.querySelectorAll(sel);
                elements.forEach(el => {
                    const text = el.innerText.trim();
                    if (text.length > 10) {
                        tareas.push({
                            texto: text.substring(0, 500),
                        });
                    }
                });
                if (tareas.length > 0) break;
            }

            if (tareas.length === 0) {
                const main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
                return [{texto: main.innerText.substring(0, 5000), fallback: true}];
            }
            return tareas;
        }
        """)

        print(f"\nElementos encontrados: {len(tareas)}")
        for i, t in enumerate(tareas):
            print(f"\n--- Tarea {i+1} ---")
            print(t.get("texto", "")[:500])

        with open(TAREAS_TEAMS_PATH, "w", encoding="utf-8") as f:
            json.dump({"tareas_raw": tareas}, f, indent=2, ensure_ascii=False)

        print(f"\nDatos guardados en {TAREAS_TEAMS_PATH}")
        browser.close()
        return tareas


def ver_tarea_detalle(indice=0):
    """Abre una tarea específica y extrae los detalles."""
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel=None,
            viewport={"width": 1280, "height": 900},
            locale="es-MX",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        print("Abriendo Teams Tareas...")
        page.goto(TEAMS_ASSIGNMENTS_URL)
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        time.sleep(8)

        # Buscar cards clickeables
        cards = page.query_selector_all('[data-tid="assignment-card"], .assignment-card, [class*="assignment-list"] a, [class*="Assignment"] a, [role="listitem"] a')

        if not cards:
            cards = page.query_selector_all('a[href*="assignment"], [role="listitem"]')

        if 0 <= indice < len(cards):
            cards[indice].click()
            time.sleep(5)

            screenshot_path = BASE_DIR / "assets" / f"tarea_detalle_{indice}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot: {screenshot_path}")

            content = page.evaluate("""
            () => {
                const main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
                return main.innerText.substring(0, 8000);
            }
            """)
            print(f"\nContenido:\n{content[:3000]}")
        else:
            print(f"No se encontró tarea #{indice}. Cards: {len(cards)}")

        browser.close()


def subir_archivo(archivo_path, tarea_indice=0):
    """Abre Teams, navega a una tarea y sube el archivo."""
    archivo = Path(archivo_path)
    if not archivo.exists():
        print(f"Archivo no encontrado: {archivo_path}")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel=None,
            viewport={"width": 1280, "height": 900},
            locale="es-MX",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(TEAMS_ASSIGNMENTS_URL)
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        time.sleep(8)

        # Navegar a la tarea
        cards = page.query_selector_all('[data-tid="assignment-card"], .assignment-card, [role="listitem"] a, a[href*="assignment"]')
        if 0 <= tarea_indice < len(cards):
            cards[tarea_indice].click()
            time.sleep(5)
        else:
            print(f"Tarea #{tarea_indice} no encontrada.")
            browser.close()
            return False

        # Buscar botón de agregar trabajo
        add_selectors = [
            'button:has-text("Agregar trabajo")',
            'button:has-text("Add work")',
            'button:has-text("Adjuntar")',
            'button:has-text("Attach")',
            'button:has-text("+ Add work")',
        ]

        clicked = False
        for sel in add_selectors:
            try:
                btn = page.query_selector(sel)
                if btn:
                    btn.click()
                    clicked = True
                    time.sleep(2)
                    break
            except Exception:
                continue

        if clicked:
            # Buscar input de archivo
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(str(archivo))
                print(f"Archivo subido: {archivo.name}")
                time.sleep(5)

                # Screenshot de confirmación
                screenshot = BASE_DIR / "assets" / "teams_subido.png"
                page.screenshot(path=str(screenshot))
                print(f"Screenshot: {screenshot}")

                # Buscar botón de entregar
                submit_sels = [
                    'button:has-text("Entregar")',
                    'button:has-text("Turn in")',
                    'button:has-text("Submit")',
                ]
                for sel in submit_sels:
                    try:
                        btn = page.query_selector(sel)
                        if btn:
                            print(f"Botón de entregar encontrado. Esperando confirmación...")
                            # No hacer click automático — dejar que el usuario confirme
                            break
                    except Exception:
                        continue

                browser.close()
                return True
            else:
                print("No se encontró input de archivo.")
        else:
            print("No se encontró botón de agregar trabajo.")
            # Screenshot para diagnóstico
            screenshot = BASE_DIR / "assets" / "teams_no_boton.png"
            page.screenshot(path=str(screenshot))

        browser.close()
        return False


# ─── CLI ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("""
Teams Browser — Gestor de Tareas UTM
Uso:
  python teams_browser.py login              — Iniciar sesión en Teams
  python teams_browser.py tareas             — Ver tareas pendientes
  python teams_browser.py detalle <#>        — Ver detalle de una tarea
  python teams_browser.py subir <archivo> <#tarea>  — Subir archivo
        """)
        return

    cmd = sys.argv[1]

    if cmd == "login":
        email = sys.argv[2] if len(sys.argv) > 2 else None
        pwd = os.environ.get("TEAMS_PASSWORD")
        if not pwd and email:
            pwd = getpass.getpass("Contraseña de Teams: ")
        login(email, pwd)
    elif cmd == "tareas":
        revisar_tareas()
    elif cmd == "detalle":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        ver_tarea_detalle(idx)
    elif cmd == "subir":
        if len(sys.argv) < 3:
            print("Uso: python teams_browser.py subir <archivo> [#tarea]")
            return
        idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        subir_archivo(sys.argv[2], idx)


if __name__ == "__main__":
    main()
