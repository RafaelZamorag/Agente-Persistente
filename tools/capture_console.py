"""Captura headless de la consola para verificación visual y material de exposición.

Uso:
    /usr/bin/python3 tools/capture_console.py http://127.0.0.1:8030 salida.png
"""
import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    output = sys.argv[2] if len(sys.argv) > 2 else "console_agente.png"
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 1250})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(base_url, wait_until="networkidle")
        page.wait_for_timeout(2500)

        print("titulo:", page.title())
        print("estado:", page.inner_text("#status-pill"))
        print("proximo ciclo:", page.inner_text("#countdown"))
        print("ciclos registrados:", page.inner_text("#total-runs"))
        print("tarjetas:", page.locator(".card").count())
        print("elementos en registro:", page.locator("#runs > li").count())
        print("primera conclusion:", page.locator(".verdict").first.inner_text())
        print("barras pintadas:", page.locator(".bar-fill").first.evaluate("el => el.offsetWidth"))
        print("metricas:", " | ".join(page.inner_text(f"#{i}") for i in
                                     ("m-fixtures", "m-positive", "m-best", "m-duration")))
        print("errores de navegador:", errors or "ninguno")

        page.screenshot(path=output, full_page=True)
        browser.close()
    print("captura guardada en:", output)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
