import httpx
from flask import Flask, request, Response

app = Flask(__name__)

# Target utama yang akan di-proxy
TARGET_URL = 'https://m.facebook.com'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Meneruskan semua permintaan ke target URL"""
    
    # Bangun URL tujuan lengkap
    if path:
        destination = f"{TARGET_URL}/{path}"
    else:
        destination = TARGET_URL
    
    # Ambil query string jika ada
    if request.query_string:
        destination = f"{destination}?{request.query_string.decode('utf-8')}"
    
    # Dapatkan method HTTP (GET, POST, dll)
    method = request.method
    
    # Ambil headers, kecuali yang berhubungan dengan host
    headers = {k: v for k, v in request.headers.items() 
               if k.lower() not in ['host', 'content-length']}
    
    # Ambil body untuk POST/PUT/PATCH
    body = request.get_data()
    
    try:
        # Kirim permintaan ke target dengan timeout 30 detik
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            resp = client.request(
                method=method,
                url=destination,
                headers=headers,
                content=body if body else None
            )
        
        # Buat response Flask dari response target
        response = Response(
            response=resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('content-type', 'text/html')
        )
        
        # Salin header penting (kecuali content-length karena sudah diatur ulang)
        for key, value in resp.headers.items():
            if key.lower() not in ['content-length', 'transfer-encoding']:
                response.headers[key] = value
        
        return response
        
    except httpx.TimeoutException:
        return Response("Gateway Timeout", status=504)
    except Exception as e:
        return Response(f"Proxy Error: {str(e)}", status=502)


# Handler untuk Vercel (wajib ada)
handler = app
