from http.server import HTTPServer, SimpleHTTPRequestHandler

def run_http_server(host="0.0.0.0", port=8000):
    """
    Run an HTTP server listening on all network interfaces (IPv4 and IPv6).
    """
    class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>HTTP Server</title>
            </head>
            <body>
                <h1>Welcome to the HTTP Server!</h1>
                <p>This server is running on Python and is accessible on all interfaces.</p>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode("utf-8"))

    # Start the HTTP server
    httpd = HTTPServer((host, port), MyHTTPRequestHandler)
    print(f"HTTP Server started on {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down HTTP Server...")
        httpd.server_close()

if __name__ == "__main__":
    run_http_server(port=8000)