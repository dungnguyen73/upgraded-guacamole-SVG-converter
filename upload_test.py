import http.client, uuid
path = 'pictographic-challenge/challenge_sample/letter_H.png'
boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary}
with open(path, 'rb') as f:
    body = b''
    body += b'--' + boundary.encode() + b'\r\n'
    body += b'Content-Disposition: form-data; name="file"; filename="letter_H.png"\r\n'
    body += b'Content-Type: image/png\r\n\r\n'
    body += f.read() + b'\r\n'
    body += b'--' + boundary.encode() + b'--\r\n'
conn = http.client.HTTPConnection('localhost', 8000)
conn.request('POST', '/upload', body, headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode('utf-8', errors='replace'))
