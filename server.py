#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
    ./server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import os
import sys
import time
import parserheader
import json
import re
from lfd import lfd
from make_colors import make_colors
from debug import debug
import traceback
import configset
import pm
PID = os.getpid()
PACKAGES = ''
PACKAGE_LOCALSTORAGE = ''
config = ''
class_pm = pm.pm()

class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()

    def _response_file_static(self, file_path):
        self.send_response(200)
        if os.path.isfile(file_path):
            if file_path.endswith(".whl"):
                self.send_header('Content-type', 'application/zip')
            elif file_path.endswith(".gz"):
                self.send_header('Content-type', 'application/x-tar')
            elif file_path.endswith(".exe"):
                self.send_header('Content-type', 'application/x-msdownload')
            self.send_header('Content-Disposition',
                             'attachment; filename="%s"' % (os.path.basename(file_path)))
            self.end_headers()
    
            # not sure about this part below
            with open(file_path, 'rb') as file:
                # Read the file and send the contents
                self.wfile.write(file.read())

    def _message_pack(self, found_package_name, found_link='#', found_name='#', repeat=None):
        # repeat must be: [({'name':name, 'link': link})]
        debug(repeat = repeat)
        message = """<html><head><title>Links for %s</title></head><body>
    <h1>Links for %s</h1>
    <a href="%s">%s</a><br>
    </body></html>""" % (found_package_name, found_package_name, found_link, found_name)
        if repeat:
            message = """<html><head><title>Links for %s</title></head><body>
    <h1>Links for %s</h1>""" % (found_package_name, found_package_name)
            for i in repeat:
                message = message + \
                    """<a href="%s">%s</a><br>""" % (
                        i.get('link'), i.get('name'))
            message = message + """</body></html>"""
        debug(message = message)
        return message

    def do_GET(self):
        global PACKAGES
        global PACKAGE_LOCALSTORAGE
        global config
        global class_pm
        LFD_FOUND = False
        SPESIFIC = config.read_config('GENERAL', 'spesific', value='0')
        lfd_class = lfd()
        if os.getenv('DEBUG_EXTRA'):
            print "dir(self) =", dir(self)
            print "-" * 100
            for i in dir(self):
                print i, "=", getattr(self, i)
            print "=" * 100
        user_agent_string = parserheader.parserHeader(
            self.headers).get('User-Agent')
        user_agent, user_agent_split = parserheader.UserAgent(
            user_agent_string)
        debug(USER_AGENT_STRING = user_agent_string)
        debug(USER_AGENT = user_agent)
        debug(USER_AGENT_SPLIT = user_agent_split)
        info_header = json.loads(user_agent_split[1])
        debug(INFO_HEADER = info_header)
        debug(PATH = self.path)
        path_split = re.split('/', self.path)
        try:
            for i in path_split:
                path_split.remove('')
        except:
            pass
        debug(PATH_SPLIT = path_split)
        find_name = path_split[-1].lower()
        debug(find_name = find_name)
        #package_localstorage = lfd_class.identify_localstorage()
        if os.getenv('DEBUG_EXTRA'):
            debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
        if find_name.endswith(".gz") or find_name.endswith(".zip") or find_name.endswith(".exe"):
            find_name = path_split[-1]
            debug(find_name = find_name)
            debug(find_name = '', endswith = os.path.splitext(find_name)[1])
            found_name_localstorage = class_pm.translate(find_name)
            debug(found_name_localstorage = found_name_localstorage)
            found_package_localstorage = PACKAGE_LOCALSTORAGE.get(found_name_localstorage.lower())
            debug(found_package_localstorage = found_package_localstorage)
            if found_package_localstorage:
                for i in found_package_localstorage:
                    if os.path.basename(i) == find_name:
                        debug(i = i)
                        self._response_file_static(i)
            else:
                self.send_response(404)
        debug(SPESIFIC = SPESIFIC)
        if SPESIFIC == "1":
            find_python_version = "cp" + \
                "".join(info_header.get('python').split('.', 2)[:2])
            find_architecture = info_header.get('cpu').lower()
            if find_architecture == 'amd64':
                find_architecture = 'win_amd64'
            found_link, found_name, found_package_name = lfd_class.find(
                find_name, find_python_version, find_architecture, PACKAGES)
            message = self._message_pack(
                found_package_name, found_link, found_name)
            self._set_headers()
            self.wfile.write(message)
        else:
            packages = PACKAGES
            # repeat must be: [({'name':name, 'link': link})]
            message_repeat = []
            for i in PACKAGES:
                if PACKAGES.get(i).get('package_name') == find_name:
                    all_packages = PACKAGES.get(i).get('packages')
                    for p in all_packages:
                        message_repeat.append(
                            ({'name': all_packages.get(p).get('name'), 'link': all_packages.get(p).get('link')}))
                    LFD_FOUND = True
                    message = self._message_pack(find_name, repeat=message_repeat)
                    self._set_headers()
                    self.wfile.write(message)
        debug(LFD_FOUND = LFD_FOUND)
        if not LFD_FOUND:
            #packages = lfd_class.identify_localstorage()
            if SPESIFIC == '1':
                find_python_version = "cp" + \
                    "".join(info_header.get('python').split('.', 2)[:2])
                find_architecture = info_header.get('cpu').lower()
                if find_architecture == 'amd64':
                    find_architecture = 'win_amd64'
                if find_architecture == 'win32':
                    find_architecture = 'win32'
                if PACKAGE_LOCALSTORAGE.get(find_name):
                    file_path = lfd_class.find_localstorage(
                        find_python_version, find_architecture, PACKAGES.get(i))
                    message = self._message_pack(find_name, os.path.basename(
                        file_path), os.path.basename(file_path))
                    self._set_headers()
                    self.wfile.write(message)
                    
                else:
                    self.send_response(404)
            else:
                debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
                debug(find_name = find_name)
                found_list_package_localstorage = PACKAGE_LOCALSTORAGE.get(find_name)
                debug(found_list_package_localstorage = found_list_package_localstorage)
                # repeat must be: [({'name':name, 'link': link})]
                message_repeat = []
                if found_list_package_localstorage:
                    for i in found_list_package_localstorage:
                        message_repeat.append(({'name': os.path.basename(i), 'link':os.path.basename(i)}))
                debug(message_repeat = message_repeat)
                #if not message_repeat:
                    #self.send_response(404)
                #else:
                message = self._message_pack(find_name, repeat=message_repeat)
                debug(message = message)
                self._set_headers()
                self.wfile.write(message)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # <--- Gets the size of data
        content_length = int(self.headers['Content-Length'])
        print "content_length =", content_length
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)
        print "post_data =", post_data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def monitor_repo_dir():
    global PACKAGE_LOCALSTORAGE
    path = config.read_config('PACKAGES', 'dir')
    TOTAL = 0
    if sys.version_info.major == 3:
        def folder_size():
            total = 0
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += folder_size(entry.path)
            return total
    elif sys.version_info.major == 2:
        def folder_size():
            return os.stat(path).st_mtime
    
    #def update_package_localstorage():
    lfd_class = lfd()
            
    TOTAL = folder_size()
    while 1:
        if path:
            total1 = folder_size()
            if not total1 == TOTAL:
                print "REPO CHANGED !"
                TOTAL = total1
                PACKAGE_LOCALSTORAGE = lfd_class.identify_localstorage()
                time.sleep(1)
            else:
                time.sleep(1)
        else:
            time.sleep(1)
        if os.getenv('LFD_STOP_UPDATE') == '1':
            break

def run(server_class=HTTPServer, handler_class=S, port=80):
    global PACKAGES
    global PACKAGE_LOCALSTORAGE
    global config
    config = configset.configset()
    config.configname = 'lfd.ini'
    
    lfd_class = lfd()
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes= 3)
    t1 = pool.apply_async(lfd_class.parser_content, ())
    t2 = pool.apply_async(lfd_class.identify_localstorage, ())
    t3 = pool.apply_async(monitor_repo_dir, ())
    try:
        server_address = ('', port)
        server_address_print = server_address
        if server_address[0] == '':
            server_address_print = ('0.0.0.0', server_address[1])
        httpd = server_class(server_address, handler_class)
        print 'Starting httpd .'
        while 1:
            if not t1.get():
                sys.stdout.write(".")
                time.sleep(1)
            else:
                PACKAGES = t1.get()
                break
        while 1:
            if not t2.get():
                sys.stdout.write(".")
                time.sleep(1)
            else:
                PACKAGE_LOCALSTORAGE = t2.get()
                debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
                break
        print "Server Bind %s:%s" % server_address_print
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Server shutdown ...')
    except:
        traceback.format_exc()

if __name__ == "__main__":
    print "PID:", PID
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
    #path = r'D:\PROJECTS\python-mpd2\apps\python-mpd2'
    #monitor_repo_dir(path)