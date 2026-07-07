import cgi
import json
import os
import re
import sys
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
UPLOAD_DIR = os.path.join(REPO_ROOT, 'uploads')
UPLOAD_SVG_DIR = os.path.join(REPO_ROOT, 'upload-results')

sys.path.insert(0, SCRIPT_DIR)
import main


def _safe_filename(filename):
    name = os.path.basename(filename)
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
    return name


def _build_svg_url(filename):
    return f'/upload-results/{filename}'


class UploadHandler(SimpleHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_OPTIONS(self):
        path = self.path.split('?', 1)[0].rstrip('/')
        if path == '/upload':
            self.send_response(204)
            self._send_cors_headers()
            self.end_headers()
        else:
            super().do_OPTIONS()

    def do_POST(self):
        path = self.path.split('?', 1)[0].rstrip('/')
        if path != '/upload':
            self.send_error(404, 'Not found')
            return
        print(f'[UPLOAD] {self.client_address[0]} {self.command} {self.path}')

        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_error(400, 'Content-Type must be multipart/form-data')
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
            }
        )

        if 'file' not in form:
            self._send_json(400, {'success': False, 'error': 'No file uploaded'})
            return

        file_item = form['file']
        if not file_item.filename:
            self._send_json(400, {'success': False, 'error': 'Uploaded file missing filename'})
            return

        filename = _safe_filename(file_item.filename)
        if not filename.lower().endswith('.png'):
            self._send_json(400, {'success': False, 'error': 'Only PNG files are supported'})
            return

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(UPLOAD_SVG_DIR, exist_ok=True)

        upload_basename = f"upload_{uuid.uuid4().hex}_{filename}"
        png_path = os.path.join(UPLOAD_DIR, upload_basename)
        with open(png_path, 'wb') as out_file:
            data = file_item.file.read()
            out_file.write(data)

        svg_name = os.path.splitext(upload_basename)[0] + '.svg'
        svg_path = os.path.join(UPLOAD_SVG_DIR, svg_name)

        try:
            main.process_one(png_path, svg_path)
        except Exception as exc:
            self._send_json(500, {'success': False, 'error': str(exc)})
            return

        response = {
            'success': True,
            'filename': svg_name,
            'svg_url': _build_svg_url(svg_name),
            'png_url': f'/uploads/{upload_basename}',
            'reference_available': False,
            'reference_message': 'No reference SVG was available for this upload. The generated SVG is ready for preview and download.',
            'mode': 'upload-only',
        }
        self._send_json(200, response)

    def translate_path(self, path):
        result = super().translate_path(path)
        return result


def run_server(port=8000):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(UPLOAD_SVG_DIR, exist_ok=True)

    os.chdir(REPO_ROOT)
    server = HTTPServer(('0.0.0.0', port), UploadHandler)
    print(f'Serving repository at http://localhost:{port}/')
    print('Use /index.html to access the evaluation dashboard.')
    server.serve_forever()


if __name__ == '__main__':
    run_server()
