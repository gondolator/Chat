import sys
import ssl

# Settings
listen_target = ('localhost', 9999)  # https://localhost:9999/
certificate_file = './certificate.pem'
private_key_file = './privkey.pem'

# Python 3 version
if sys.version_info[0] == 3:
    import http.server
    httpd = http.server.HTTPServer(listen_target, http.server.SimpleHTTPRequestHandler)
# Python 2 version
elif sys.version_info[0] == 2:
    import BaseHTTPServer, SimpleHTTPServer
    httpd = BaseHTTPServer.HTTPServer(listen_target, SimpleHTTPServer.SimpleHTTPRequestHandler)

# Wrap the socket with SSL
httpd.socket = ssl.wrap_socket(httpd.socket,
               certfile=certificate_file, keyfile=private_key_file, server_side=True)

# Start listening
httpd.serve_forever()