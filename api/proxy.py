# api/proxy.py
from http.client import HTTPSConnection
from urllib.parse import urlparse
import sys

def handler(request, response):
    target_url = 'https://m.facebook.com' + request.get('path', '')
    parsed_url = urlparse(target_url)
    conn = HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path + '?' + parsed_url.query)
    resp = conn.getresponse()
    response.set_header('Content-Type', 'text/html')
    response.send(resp.read())
