import argparse
import binascii
import json
from base64 import b64decode
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from anthropic import Anthropic

PROMPT = (
    "Rephrase the question in the image and options if given. "
    "Answer the question two lines below behind 'Answer:'. "
    "Keep your answer concise and to the point. Do not mention the image."
)


class WebAppHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/answer":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            self._send_json({"error": "Request body is required."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload."}, HTTPStatus.BAD_REQUEST)
            return

        api_key = payload.get("apiKey")
        image_data = payload.get("image")

        if not api_key:
            self._send_json({"error": "Anthropic API key is required."}, HTTPStatus.BAD_REQUEST)
            return

        if not image_data:
            self._send_json({"error": "Image is required."}, HTTPStatus.BAD_REQUEST)
            return

        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.split(",", 1)[1]
        elif "," in image_data:
            self._send_json({"error": "Image must be a PNG data URL or raw base64 data."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            b64decode(image_data, validate=True)
        except (binascii.Error, ValueError):
            self._send_json({"error": "Image must be valid base64 data."}, HTTPStatus.BAD_REQUEST)
            return

        try:
            client = Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data,
                                },
                            },
                        ],
                    }
                ],
            )
            answer = message.content[0].text
        except Exception:
            self._send_json({"error": "Anthropic request failed."}, HTTPStatus.BAD_GATEWAY)
            return

        self._send_json({"answer": answer}, HTTPStatus.OK)

    def _send_json(self, payload, status_code):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def run_server(host: str, port: int):
    web_dir = Path(__file__).parent / "web"
    def make_handler(*args, **kwargs):
        return WebAppHandler(*args, directory=str(web_dir), **kwargs)

    server = ThreadingHTTPServer((host, port), make_handler)
    print(f"Serving web app at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Screenshot Question Answerer web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    run_server(args.host, args.port)
