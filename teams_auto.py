#!/usr/bin/env python3
"""
Teams automático — login + extracción de tareas, headless.
Hace login fresco cada vez (sesión no persiste en headless nuevo).
"""

import getpass
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"
TAREAS_PATH = BASE_DIR / "tareas_teams.json"

EMAIL = os.environ.get("TEAMS_EMAIL", "24090714@alumno.utmetropolitana.edu.mx")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def _login(page, password):
    """Login completo a Teams."""
    page.goto("https://teams.microsoft.com")
    time.sleep(5)

    # Email
    try:
        ei = page.wait_for_selector('input[type="email"]', timeout=8000)
        ei.fill(EMAIL)
        time.sleep(1)
        page.click('input[type="submit"]')
        time.sleep(5)
    except Exception:
        # Tal vez ya hay cuenta guardada
        acct = page.query_selector(f'[data-test-id="{EMAIL}"]')
        if acct:
            acct.click()
            time.sleep(5)

    # Password
    pwd = page.wait_for_selector('input[type="password"]', timeout=15000)
    pwd.fill(password)
    time.sleep(1)
    sub = page.query_selector('input[type="submit"]')
    if sub:
        sub.click()
    time.sleep(8)

    # Stay signed in
    try:
        stay = page.wait_for_selector('#idSIButton9', timeout=5000)
        if stay:
            stay.click()
        time.sleep(5)
    except Exception:
        pass

    # Esperar Teams
    time.sleep(10)


def _extraer_texto_limpio(page):
    """Extrae texto limpio de todos los frames."""
    all_text = ""
    for frame in page.frames:
        try:
            text = frame.evaluate("() => document.body ? document.body.innerText : ''")
            if text.strip() and len(text) > 20:
                all_text += text + "\n"
        except Exception:
            pass

    lines = all_text.split("\n")
    skip = ["var ", "!function", "(function", "access_token", "eyJ", "baseUrl",
            "require", "CkQ", "driveUrl", "{", "window.", "if(", "for("]
    clean = []
    for l in lines:
        l = l.strip()
        if not l or len(l) > 200:
            continue
        if any(l.startswith(s) or s in l for s in skip):
            continue
        clean.append(l)
    return clean


def revisar(password):
    """Revisa todas las tareas (vencidas y próximas)."""
    with sync_playwright() as p:
        session_dir = str(BASE_DIR / ".ts_run")
        os.makedirs(session_dir, mode=0o700, exist_ok=True)
        os.chmod(session_dir, 0o700)
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=True,
            args=[],
            viewport={"width": 1280, "height": 900},
            user_agent=UA,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        _login(page, password)

        # Ir a Tareas
        btn = page.query_selector('button:has-text("Assignments"), button:has-text("Tareas")')
        if btn:
            btn.click()
            time.sleep(10)

        # Screenshot general
        page.screenshot(path=str(ASSETS / "teams_tareas.png"))

        # Extraer texto de la vista general
        general = _extraer_texto_limpio(page)

        # Click en tab Vencida
        vbtn = page.query_selector('button:has-text("Vencida"), button:has-text("Past due")')
        if vbtn:
            vbtn.click()
            time.sleep(8)
            page.screenshot(path=str(ASSETS / "teams_vencidas.png"))

        vencidas = _extraer_texto_limpio(page)

        # Click en tab Próximamente
        pbtn = page.query_selector('button:has-text("Próximamente"), button:has-text("Upcoming")')
        if pbtn:
            pbtn.click()
            time.sleep(8)
            page.screenshot(path=str(ASSETS / "teams_proximas.png"))

        proximas = _extraer_texto_limpio(page)

        resultado = {
            "general": "\n".join(general[:30]),
            "vencidas": "\n".join(vencidas[:30]),
            "proximas": "\n".join(proximas[:30]),
        }

        with open(TAREAS_PATH, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)

        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        ctx.close()
        return resultado


if __name__ == "__main__":
    password = os.environ.get("TEAMS_PASSWORD")
    if not password:
        password = getpass.getpass("Contraseña de Teams: ")
    revisar(password)
