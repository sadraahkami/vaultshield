"""
Lightweight REST Web Server and Static Asset Handler for VaultShield.
"""

import base64
import json
import mimetypes
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

from ..core.metadata_wiper import MetadataWiper
from ..core.steganography import SteganographyVault
from ..core.validator import FileValidator, FileCategory

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    STATIC_DIR = Path(sys._MEIPASS) / "src" / "web" / "static"
else:
    STATIC_DIR = Path(__file__).resolve().parent / "static"


class VaultShieldHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        url_path = self.path.split("?")[0]

        if url_path == "/" or url_path == "":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        if url_path == "/api/health":
            self._send_json({"status": "ok", "app": "VaultShield Privacy Studio", "version": "1.0.0"})
            return

        clean_path = url_path.lstrip("/")
        target_static = STATIC_DIR / clean_path
        if target_static.exists() and target_static.is_file():
            mime, _ = mimetypes.guess_type(str(target_static))
            if clean_path.endswith(".js"):
                mime = "application/javascript"
            elif clean_path.endswith(".css"):
                mime = "text/css"
            self._serve_file(target_static, mime or "application/octet-stream")
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/wipe":
            self._handle_api_wipe()
            return
        elif self.path == "/api/hide":
            self._handle_api_hide()
            return
        elif self.path == "/api/extract":
            self._handle_api_extract()
            return

        self.send_error(404, "Endpoint Not Found")

    def _serve_file(self, file_path: Path, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _handle_api_wipe(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self._send_json({"error": "Empty payload"}, 400)
            return

        raw_data = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return

        file_b64 = payload.get("fileData", "")
        file_name = payload.get("fileName", "input_file.jpg")

        if not file_b64:
            self._send_json({"error": "No file data provided"}, 400)
            return

        if "," in file_b64:
            file_b64 = file_b64.split(",", 1)[1]

        temp_dir = tempfile.mkdtemp(prefix="vault_wipe_")
        try:
            file_bytes = base64.b64decode(file_b64)
            ext = Path(file_name).suffix or ".jpg"
            src_path = os.path.join(temp_dir, f"input{ext}")
            with open(src_path, "wb") as f:
                f.write(file_bytes)

            dst_path = os.path.join(temp_dir, f"cleaned_{Path(file_name).stem}{ext}")
            report = MetadataWiper.wipe_metadata(src_path, dst_path)

            with open(dst_path, "rb") as f:
                cleaned_bytes = f.read()

            mime, _ = mimetypes.guess_type(dst_path)
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="cleaned_{Path(file_name).name}"')
            self.send_header("Content-Length", str(len(cleaned_bytes)))
            self.end_headers()
            self.wfile.write(cleaned_bytes)

        except Exception as e:
            self._send_json({"error": str(e)}, 500)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _handle_api_hide(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return

        carrier_b64 = payload.get("carrierData", "")
        secret_text = payload.get("secretText", "")
        passphrase = payload.get("passphrase", "")

        if not carrier_b64 or not passphrase or not secret_text:
            self._send_json({"error": "Carrier image, secret text, and passphrase are required."}, 400)
            return

        if "," in carrier_b64:
            carrier_b64 = carrier_b64.split(",", 1)[1]

        temp_dir = tempfile.mkdtemp(prefix="vault_hide_")
        try:
            carrier_bytes = base64.b64decode(carrier_b64)
            carrier_path = os.path.join(temp_dir, "cover.png")
            with open(carrier_path, "wb") as f:
                f.write(carrier_bytes)

            out_path = os.path.join(temp_dir, "stego_vault.png")
            SteganographyVault.hide_payload(
                carrier_image_path=carrier_path,
                output_image_path=out_path,
                passphrase=passphrase,
                secret_data=secret_text.encode("utf-8")
            )

            with open(out_path, "rb") as f:
                stego_bytes = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Disposition", 'attachment; filename="stego_vault.png"')
            self.send_header("Content-Length", str(len(stego_bytes)))
            self.end_headers()
            self.wfile.write(stego_bytes)

        except Exception as e:
            self._send_json({"error": str(e)}, 500)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _handle_api_extract(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return

        stego_b64 = payload.get("stegoData", "")
        passphrase = payload.get("passphrase", "")

        if not stego_b64 or not passphrase:
            self._send_json({"error": "Stego image and passphrase are required."}, 400)
            return

        if "," in stego_b64:
            stego_b64 = stego_b64.split(",", 1)[1]

        temp_dir = tempfile.mkdtemp(prefix="vault_ext_")
        try:
            stego_bytes = base64.b64decode(stego_b64)
            stego_path = os.path.join(temp_dir, "stego.png")
            with open(stego_path, "wb") as f:
                f.write(stego_bytes)

            stego_payload = SteganographyVault.extract_payload(stego_path, passphrase)

            self._send_json({
                "success": True,
                "text": stego_payload.text,
                "isFile": stego_payload.is_file,
                "filename": stego_payload.filename
            })

        except Exception as e:
            self._send_json({"error": str(e)}, 400)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _send_json(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_web_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    server_address = (host, port)
    try:
        httpd = HTTPServer(server_address, VaultShieldHttpHandler)
    except OSError:
        port = 8081
        server_address = (host, port)
        httpd = HTTPServer(server_address, VaultShieldHttpHandler)

    url = f"http://{host}:{port}"
    print("==================================================")
    print(f"[*] VaultShield Web Studio running at: {url}")
    print(f"[*] Press Ctrl+C in terminal to stop server.")
    print("==================================================")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping VaultShield web server...")
        httpd.server_close()
