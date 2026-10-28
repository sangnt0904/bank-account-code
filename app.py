from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <title>Bank Portal - Dang ky tai khoan</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: #0f172a; 
            color: #f8fafc; 
            padding: 40px; 
            display: flex; 
            justify-content: center; 
        }
        .card { 
            width: 380px; 
            background: #1e293b; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); 
        }
        h2 { color: #38bdf8; margin-top: 0; text-align: center; }
        .form-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-size: 14px; color: #cbd5e1; }
        input[type="text"], input[type="password"] { 
            width: 100%; 
            padding: 10px; 
            background: #0f172a; 
            color: #fff; 
            border: 1px solid #475569; 
            border-radius: 6px; 
            box-sizing: border-box; 
        }
        button { 
            width: 100%; 
            background: #0284c7; 
            color: #fff; 
            border: none; 
            padding: 12px; 
            border-radius: 6px; 
            font-weight: bold; 
            cursor: pointer; 
            margin-top: 10px; 
        }
        button:hover { background: #0369a1; }
        #message { 
            margin-top: 18px; 
            padding: 12px; 
            border-radius: 6px; 
            display: none; 
            font-size: 14px; 
            text-align: center; 
        }
        .success { background: #064e3b; border: 1px solid #10b981; color: #6ee7b7; }
        .error { background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🏦 Đăng ký tài khoản</h2>
        <div class="form-group">
            <label for="username">Tên đăng nhập (Username):</label>
            <input type="text" id="username" placeholder="Nhập username...">
        </div>
        <div class="form-group">
            <label for="password">Mật khẩu (Password):</label>
            <input type="password" id="password" placeholder="Nhập password...">
        </div>
        <button onclick="register()">Tạo tài khoản</button>
        <div id="message"></div>
    </div>

    <script>
        function register() {
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value.trim();
            const msg = document.getElementById('message');

            if (!u || !p) {
                msg.className = 'error';
                msg.style.display = 'block';
                msg.innerText = 'Vui lòng điền đầy đủ Username và Password!';
                return;
            }

            fetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            })
            .then(r => r.json())
            .then(data => {
                msg.style.display = 'block';
                msg.className = 'success';
                msg.innerText = '✅ ' + data.message;
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
            })
            .catch(() => {
                msg.style.display = 'block';
                msg.className = 'error';
                msg.innerText = 'Có lỗi xảy ra khi kết nối máy chủ!';
            });
        }
    </script>
</body>
</html>"""

users_db = []

class BankRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/register':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                username = data.get('username')
                password = data.get('password')

                users_db.append({'username': username, 'password': password})
                print(f"[REGISTER AUDIT] Tạo thành công tài khoản: {username}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {'message': f'Đăng ký tài khoản "{username}" thành công!'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print("Server running on port 8080...")
    HTTPServer(('0.0.0.0', 8080), BankRequestHandler).serve_forever()