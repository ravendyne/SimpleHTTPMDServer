#!/usr/bin/python

#https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import SimpleHTTPServer
import SocketServer

import pycurl
from StringIO import StringIO
import json

import os
import sys


import mdconfig as conf



PORT = conf.port

GITHUB_PERSONAL_ACCESS_TOKEN = conf.githubToken
GITHUB_USER_PASSWORD = conf.githubUser + ':' + conf.githubPassword if conf.githubUser and conf.githubPassword else ''
CONTENT_TYPE = 'text/x-markdown'
USER_AGENT = conf.userAgent #'SimpleHTTPServer 1.0'
API_URL = conf.githubApiUrl #'https://api.github.com/markdown'


__location__ = os.path.realpath(os.path.dirname(__file__))
MARKDOWN_BODY_CSS = open(os.path.join(__location__, 'files/markdown_body.css'), 'r').read()
GITHUB_MARKDOWN_CSS = open(os.path.join(__location__, 'files/github_markdown.css'), 'r').read()
HTML_HEAD = open(os.path.join(__location__, 'files/head.html'), 'r').read()
HTML_TAIL = open(os.path.join(__location__, 'files/tail.html'), 'r').read()



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

    data = {
#        'mode': 'markdown',
        'mode': 'gfm',
        'text': markdownContent
    }
    postData = json.dumps(data)

    c = pycurl.Curl()

    c.setopt(c.URL, API_URL)
    c.setopt(c.POST, True)
    if GITHUB_USER_PASSWORD:
        c.setopt(c.USERPWD, GITHUB_USER_PASSWORD)
    c.setopt(c.HTTPHEADER, headers)
    #c.setopt(c.POSTFIELDS, markdownContent)
    c.setopt(c.POSTFIELDS, postData)
    #c.setopt(c.WRITEDATA, buffer)
    #or
    c.setopt(c.WRITEFUNCTION, buffer.write)
    #if you need headers
    c.setopt(c.HEADERFUNCTION, header.write)

    #for debugging
    #c.setopt(c.VERBOSE, True)
    c.perform()
    c.close()

    body = buffer.getvalue()

    return body

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = remove_prefix(self.path, '/')

        if self.path.endswith(".md"):
            convertedMarkdown = getGFM(path)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()

            self.wfile.write(HTML_HEAD)
            self.wfile.write('<style>')
            self.wfile.write(GITHUB_MARKDOWN_CSS)
            self.wfile.write('</style>')
            self.wfile.write('<style>')
            self.wfile.write(MARKDOWN_BODY_CSS)
            self.wfile.write('</style>')
            self.wfile.write('<article class="markdown-body">')
            self.wfile.write(convertedMarkdown,)
            self.wfile.write('</article>')
            self.wfile.write(HTML_TAIL)
            self.wfile.close()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# if the script is called with user:pass parameter, get it
# if not, we'll use anonymous access which is limited to 60 calls per hour
for arg in sys.argv:
    print arg
    if ":" in arg:
        GITHUB_USER_PASSWORD = arg


Handler = MyRequestHandler


httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at http://127.0.0.1:%s/" % PORT
httpd.serve_forever()

