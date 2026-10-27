from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bank Data Leak Scanner</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }
        .card { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 25px; border-radius: 10px; }
        h2 { color: #38bdf8; margin-top: 0; }
        textarea { width: 100%; height: 110px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 6px; padding: 10px; box-sizing: border-box; }
        button { background: #0284c7; color: #fff; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 12px; }
        button:hover { background: #0369a1; }
        #res { margin-top: 20px; padding: 12px; border-radius: 6px; display: none; line-height: 1.6; }
        .danger { background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; }
        .safe { background: #064e3b; border: 1px solid #10b981; color: #6ee7b7; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ Bank Data Leak Scanner</h2>
        <p style="color: #94a3b8; font-size: 13px;">Ứng dụng chạy từ container image do OpenShift BuildConfig tự động đóng gói</p>
        <textarea id="txt" placeholder="Dán văn bản cần kiểm tra (ví dụ: Thẻ 4532-1234-5678-9012 hoặc CCCD 079123456789)..."></textarea><br>
        <button onclick="scan()">Quét rò rỉ dữ liệu</button>
        <div id="res"></div>
    </div>
    <script>
        function scan() {
            fetch('/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: document.getElementById('txt').value})
            })
            .then(r => r.json())
            .then(d => {
                const el = document.getElementById('res');
                el.style.display = 'block';
                if (d.leaks.length > 0) {
                    el.className = 'danger';
                    el.innerHTML = '<strong>⚠️ PHÁT HIỆN LỘ DỮ LIỆU:</strong><br>' + d.leaks.join('<br>');
                } else {
                    el.className = 'safe';
                    el.innerHTML = '<strong>✅ AN TOÀN:</strong> Không phát hiện dữ liệu nhạy cảm.';
                }
            });
        }
    </script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/scan':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                text = json.loads(body).get('text', '')
            except:
                text = body

            leaks = []
            # Quét số thẻ tín dụng/ghi nợ (16 số)
            cards = re.findall(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', text)
            if cards:
                leaks.append(f"• Số thẻ thanh toán: {', '.join(cards)}")

            # Quét số CCCD (12 số)
            cccd = re.findall(r'\b0\d{11}\b', text)
            if cccd:
                leaks.append(f"• Số định danh CCCD: {', '.join(cccd)}")

            # Quét Email
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
            if emails:
                leaks.append(f"• Email: {', '.join(emails)}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'leaks': leaks}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print("Server running on port 8080...")
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()