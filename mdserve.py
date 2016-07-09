#!/usr/bin/python

import SimpleHTTPServer
import SocketServer

import pycurl
from StringIO import StringIO

PORT = 8888

GITHUB_PERSONAL_ACCESS_TOKEN = ''
#or
GITHUB_USER_PASSWORD = 'emengine:AMDathlon4321'
CONTENT_TYPE = 'text/x-markdown'
USER_AGENT = 'SimpleHTTPServer 1.0'
API_URL = 'https://api.github.com/markdown/raw'

HTML_HEAD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>GitHub Markdown render</title>
</head>
<body>
"""
HTML_TAIL = """
</body>
</html>
"""

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def getGFM(filePath):
    buffer = StringIO()
    header = StringIO()


    with open(filePath, 'r') as content_file:
        markdownContent = content_file.read()

    headers = [
    #    'Authorization: token ' + GITHUB_PERSONAL_ACCESS_TOKEN,
        'Content-Type: ' + CONTENT_TYPE,
        'User-Agent: ' + USER_AGENT
    ]

    c = pycurl.Curl()

    c.setopt(c.URL, API_URL)
    c.setopt(c.POST, True)
    c.setopt(c.USERPWD, GITHUB_USER_PASSWORD)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.POSTFIELDS, markdownContent)
    #c.setopt(c.WRITEDATA, buffer)
    #or
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.HEADERFUNCTION, header.write)

    #c.setopt(c.VERBOSE, True)
    c.perform()
    c.close()

    body = buffer.getvalue()

    return body

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = remove_prefix(self.path, '/')
        #print('self.path = ' + path)

        if self.path.endswith(".md"):
            convertedMarkdown = getGFM(path)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()

            self.wfile.write(HTML_HEAD);
            self.wfile.write(convertedMarkdown);
            self.wfile.write(HTML_TAIL);
            self.wfile.close();
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = MyRequestHandler


httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at port", PORT
httpd.serve_forever()

