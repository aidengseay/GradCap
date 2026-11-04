# ==============================================================================
# Server Imports
# ==============================================================================

import os
import wifi
import socketpool

from adafruit_httpserver import (
    Server,
    Request,
    FileResponse,
    JSONResponse,
    POST,
)

# ==============================================================================
# Server Constants
# ==============================================================================

SSID = os.getenv("GRADCAP_AP_SSID")
PASSWORD = os.getenv("GRADCAP_AP_PASSWORD")

PORT = 5000
WEB_ROOT = "/web"

ANIMATIONS = {
    "pong-test": "pong-test.gif",
    "cat-space": "cat-space.gif",
}

# ==============================================================================
# Server Helper Functions
# ==============================================================================

def start_wifi():
    
    # Create the GradCap Wi-Fi access point

    if not SSID or not PASSWORD:
        raise RuntimeError("Missing Wi-Fi credentials")

    if len(PASSWORD) < 8:
        raise ValueError("Wi-Fi password too short")

    wifi.radio.start_ap(
        ssid=SSID,
        password=PASSWORD,
    )

    ip_address = str(wifi.radio.ipv4_address_ap)

    print("SSID:", SSID)
    print("IP:", ip_address)

    return ip_address


def error_response(request, message, status=400):
    
    # Return an HTTP error response for improper request

    reasons = {
        400: "Bad Request",
        500: "Internal Server Error",
    }

    return JSONResponse(
        request,
        {"error": message},
        status=(status, reasons.get(status, "Error")),
    )


def parse_json(request):

    # Parse a JSON request body

    try:
        data = request.json()
    except (ValueError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    return data


def valid_hex_color(value):
    
    # Validate a color string 

    if not isinstance(value, str):
        return False

    if len(value) != 7 or value[0] != "#":
        return False

    for char in value[1:]:
        if char not in "0123456789abcdefABCDEF":
            return False

    return True

# ==============================================================================
# Server Endpoints
# ==============================================================================

def create_server(controller):
    
    # Register website and API routes

    pool = socketpool.SocketPool(wifi.radio)

    http_server = Server(
        pool,
        root_path=WEB_ROOT,
        debug=False,
    )

    # ---------------------------------
    # Website
    # ---------------------------------

    @http_server.route("/")
    def index(request: Request):
        return FileResponse(
            request,
            "index.html",
            root_path=WEB_ROOT,
        )

    @http_server.route("/style.css")
    def stylesheet(request: Request):
        return FileResponse(
            request,
            "style.css",
            root_path=WEB_ROOT,
        )

    @http_server.route("/app.js")
    def javascript(request: Request):
        return FileResponse(
            request,
            "app.js",
            root_path=WEB_ROOT,
        )

    # ---------------------------------
    # POST /api/text
    # ---------------------------------

    @http_server.route("/api/text", POST)
    def handle_text(request: Request):
        data = parse_json(request)

        if data is None:
            return error_response(request, "Invalid JSON")

        text = data.get("text")
        color = data.get("color")

        if not isinstance(text, str) or not text.strip():
            return error_response(request, "Invalid text")

        if len(text) > 200:
            return error_response(request, "Text too long")

        if not valid_hex_color(color):
            return error_response(request, "Invalid color")

        controller.set_text(
            text.strip(),
            int(color[1:], 16),
        )

        return JSONResponse(
            request,
            {"status": "ok"},
        )

    # ---------------------------------
    # POST /api/clear
    # ---------------------------------

    @http_server.route("/api/clear", POST)
    def handle_clear(request: Request):

        # Get the matrix to clear the screen
        controller.clear()

        return JSONResponse(
            request,
            {"status": "ok"},
        )

    # ---------------------------------
    # POST /api/brightness
    # ---------------------------------

    @http_server.route("/api/brightness", POST)
    def handle_brightness(request: Request):
        data = parse_json(request)

        if data is None:
            return error_response(request, "Invalid JSON")

        brightness = data.get("brightness")

        if isinstance(brightness, bool) or not isinstance(
            brightness, (int, float)
        ):
            return error_response(
                request,
                "Invalid brightness",
            )

        if not 0.0 <= brightness <= 1.0:
            return error_response(
                request,
                "Brightness must be between 0 and 1",
            )

        # Change the brightness of the LEDs
        controller.set_brightness(brightness)

        return JSONResponse(
            request,
            {"status": "ok"},
        )

    # ---------------------------------
    # POST /api/animation
    # ---------------------------------

    @http_server.route("/api/animation", POST)
    def handle_animation(request: Request):
        data = parse_json(request)

        if data is None:
            return error_response(request, "Invalid JSON")

        animation = data.get("animation")

        if animation not in ANIMATIONS:
            return error_response(
                request,
                "Unknown animation",
            )

        # Start a pre-made animation
        controller.set_animation(ANIMATIONS[animation])

        return JSONResponse(
            request,
            {"status": "ok"},
        )

    return http_server

# ==============================================================================
# Server Startup & Loop
# ==============================================================================

def run(controller):
    
    # Start networking and run the server loop

    ip_address = start_wifi()
    http_server = create_server(controller)

    http_server.start(
        host=ip_address,
        port=PORT,
    )

    while True:
        http_server.poll()
        controller.update()
