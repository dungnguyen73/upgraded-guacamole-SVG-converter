import http.client
import json
import os
import sys
import threading
import unittest
from http.server import HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upload_server


class UploadServerTests(unittest.TestCase):
    def test_upload_response_marks_missing_reference_as_upload_only(self):
        sample_png = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'pictographic-challenge',
            'challenge_sample',
            'letter_H.png',
        )
        self.assertTrue(os.path.exists(sample_png), sample_png)

        server = HTTPServer(('127.0.0.1', 0), upload_server.UploadHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            boundary = '----WebKitFormBoundary' + 'testboundary123'
            headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary}
            with open(sample_png, 'rb') as handle:
                body = (
                    b'--' + boundary.encode() + b'\r\n'
                    + b'Content-Disposition: form-data; name="file"; filename="letter_H.png"\r\n'
                    + b'Content-Type: image/png\r\n\r\n'
                    + handle.read() + b'\r\n'
                    + b'--' + boundary.encode() + b'--\r\n'
                )

            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=10)
            conn.request('POST', '/upload', body, headers)
            response = conn.getresponse()
            payload = json.loads(response.read().decode('utf-8'))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(response.status, 200)
        self.assertTrue(payload['success'])
        self.assertFalse(payload['reference_available'])
        self.assertIn('reference', payload['reference_message'].lower())


if __name__ == '__main__':
    unittest.main()
