#!/usr/bin/python

#https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import os
import sys

import SimpleHTTPServer
import BaseHTTPServer
import ConfigParser
import argparse

import pycurl
from StringIO import StringIO
import json


parser = argparse.ArgumentParser(description='SimpleHTTPMDServer to serve formatted Github flavored Markdown files.')
parser.add_argument('-b,', '--bind', help='ip address to bind to, i.e. 192.168.0.25', default='127.0.0.1')
parser.add_argument('-t,', '--port', help='port to use, i.e. 8090', type=int, default=8000)
parser.add_argument('-u,', '--user', help='github user for API authentication', default='')
parser.add_argument('-p,', '--password', help="github user's password for API authentication", default='')

Config = ConfigParser.ConfigParser()
Config.read("server.conf")

args = parser.parse_args()
server_options = dict(Config.items('server'))
github_options = dict(Config.items('github'))

print server_options
print github_options

# server config
HOST = server_options['host'] if 'host' in server_options else args.bind
PORT = server_options['port'] if 'port' in server_options else args.port
USER_AGENT = server_options['user-agent'] if 'user-agent' in server_options else 'SimpleHTTPServer 1.0'


# github config
API_URL = github_options['github-api-url'] # i.e. 'https://api.github.com/markdown'

GITHUB_PERSONAL_ACCESS_TOKEN = github_options['github-token'] if 'github-token' in github_options else ''

GITHUB_USER = github_options['github-user'] if 'github-user' in github_options else args.user
GITHUB_PASSWORD = github_options['github-password'] if 'github-password' in github_options else args.password

GITHUB_USER_PASSWORD = GITHUB_USER + ':' + GITHUB_PASSWORD if GITHUB_USER and GITHUB_PASSWORD else ''

CONTENT_TYPE = 'text/x-markdown'


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


httpd = BaseHTTPServer.HTTPServer((HOST, PORT), MyRequestHandler)

print "Serving at http://%s:%s/" % (HOST, PORT)
httpd.serve_forever()

