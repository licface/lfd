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
from SocketServer import ThreadingMixIn
# import threading
import os
import sys
import time
import parserheader
import json
import re
from lfd import lfd
# from make_colors import make_colors
from debug2 import debug 
import traceback
import configset
import pm
import vping
import socket
import sendgrowl
from multiprocessing.pool import ThreadPool
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AbsoluteETA, AdaptiveTransferSpeed

MAXVAL=100
EVENT="UPDATE REPO"
WIDGETS = ['%s: '%(EVENT), Percentage(), ' | ', ETA(), ' | ', AbsoluteETA()]
PBAR = ProgressBar(widgets=WIDGETS, maxval=MAXVAL)

PID = os.getpid()
PACKAGES = ''
PACKAGE_LOCALSTORAGE = ''
SCAN_FINISHED = False
config = configset.configset()
config.configname = 'lfd.ini'
class_pm = pm.pm()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class S(BaseHTTPRequestHandler):
    
    # def debug_server_client(self, msg, server_host = '127.0.0.1', port = 50001):
    #     global config
    #     DEBUG_SERVER = config.read_config('DEBUG', 'HOST', value='%s:%s'%(server_host, str(port)))
    #     print "DEBUG_SERVER =", DEBUG_SERVER
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     if DEBUG_SERVER:
    #         if ":" in DEBUG_SERVER:
    #             host, port = str(DEBUG_SERVER).strip().split(":")
    #             port = int(port.strip())
    #             host = host.strip()
    #         else:
    #             host = DEBUG_SERVER.strip()
    #         print "host =", host
    #         print "port =", port
    #         s.sendto(msg, (host, int(port)))
    #         s.close()

    # def debug(self, defname = None, debug_this = None, debug_server = False, line_number = '', print_function_parameters = False, **kwargs):
    #     msg = debug(defname, debug_this, debug_server, line_number, print_function_parameters, no_debugserver=True, **kwargs)
    #     self.debug_server_client(msg)

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(150)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.send_header("Connection", "keep-alive")
        self.send_header("keep-alive", "timeout=60, max=30")
        self.end_headers()

    def _response_file_static(self, file_path):
        if os.path.isfile(file_path):
            self.send_response(200)
            debug(file_path_is_file=os.path.isfile(file_path))
            if file_path.endswith(".whl"):
                # self.send_header('Content-type', "application/octet-stream")
                self.send_header('Content-type', "application/zip")
            elif file_path.endswith(".gz"):
                self.send_header('Content-type', 'application/x-tar')
            elif file_path.endswith(".exe"):
                self.send_header('Content-type', 'application/x-msdownload')
            self.send_header("Connection", "keep-alive")
            self.send_header("keep-alive", "timeout=60, max=30")
            self.send_header('Content-Disposition',
                             'attachment; filename="%s"' % (os.path.basename(file_path)))
            
    
            # not sure about this part below
            with open(file_path, 'rb') as file:
                # Read the file and send the contents
                file_read = file.read()
                file_length = len(file_read)
                self.send_header("Content-Length", file_length)
                self.end_headers()
                self.wfile.write(file_read)
        else:
            self.send_response(400)

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
        STORAGE_FOUND = False
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
        message_repeat_localstorage = []
        message_repeat_lfd = []
        message_repeat_all = []
        print "self_header =", self.headers

        # if not LFD_FOUND:
        debug(SPESIFIC = SPESIFIC)
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
                # message = self._message_pack(find_name, os.path.basename(
                    # file_path), os.path.basename(file_path))
                # self._set_headers()
                # self.wfile.write(message)
                message_repeat_localstorage.append(({'name':find_name, 'link':os.path.basename(find_name)}))
                STORAGE_FOUND = True
            # else:
                # self.send_response(404)

            # if SPESIFIC == "1":
            # find_python_version = "cp" + \
            #     "".join(info_header.get('python').split('.', 2)[:2])
            # find_architecture = info_header.get('cpu').lower()
            # if find_architecture == 'amd64':
            #     find_architecture = 'win_amd64'
            found_link, found_name, found_package_name = lfd_class.find(
                find_name, find_python_version, find_architecture, PACKAGES)
            if found_link:
                LFD_FOUND = True
                message_repeat_lfd.append(({'name':found_name, 'link': found_link}))

            # message = self._message_pack(
                # found_package_name, found_link, found_name)
            # self._set_headers()
            # self.wfile.write(message)
        else:
            if os.getenv('DEBUG_EXTRA'):
                debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
            debug(find_name = find_name)
            found_list_package_localstorage = PACKAGE_LOCALSTORAGE.get(find_name)
            debug(found_list_package_localstorage = found_list_package_localstorage)
            if not found_list_package_localstorage:
                found_list_package_localstorage = PACKAGE_LOCALSTORAGE.get(str(find_name).replace("-", "."))
            debug(found_list_package_localstorage_changed = found_list_package_localstorage)
            # repeat must be: [({'name':name, 'link': link})]
            # message_repeat = []
            if found_list_package_localstorage:
                STORAGE_FOUND = True
                for i in found_list_package_localstorage:
                    # message_repeat.append(({'name': os.path.basename(i), 'link':os.path.basename(i)}))
                    message_repeat_localstorage.append(({'name': os.path.basename(i), 'link':os.path.basename(i)}))
                    debug(message_repeat_localstorage=message_repeat_localstorage)
            # debug(message_repeat = message_repeat)
            #if not message_repeat:
                #self.send_response(404)
            #else:
            # message = self._message_pack(find_name, repeat=message_repeat)
            # debug(message = message)
            # self._set_headers()
            # self.wfile.write(message)

            for i in PACKAGES:
                if PACKAGES.get(i).get('package_name') == find_name:
                    all_packages = PACKAGES.get(i).get('packages')
                    for p in all_packages:
                        # message_repeat.append(
                        #     ({'name': all_packages.get(p).get('name'), 'link': all_packages.get(p).get('link')}))
                        message_repeat_lfd.append(
                            ({'name': all_packages.get(p).get('name'), 'link': all_packages.get(p).get('link')}))
                        debug(message_repeat_lfd=message_repeat_lfd)
                    LFD_FOUND = True
                    # message = self._message_pack(find_name, repeat=message_repeat)
                    # self._set_headers()
                    # self.wfile.write(message)
        
        if os.getenv('DEBUG_EXTRA'):
            debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
        if find_name.endswith(".gz") or find_name.endswith(".whl") or find_name.endswith(".zip") or find_name.endswith(".exe"):
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
        # else:

            # else:
            # packages = PACKAGES
            # repeat must be: [({'name':name, 'link': link})]
            # message_repeat = []
            
            # debug(LFD_FOUND = LFD_FOUND)
        else:
            debug("BEGIN MESSAGE PACK")
            debug(STORAGE_FOUND=STORAGE_FOUND)
            debug(LFD_FOUND=LFD_FOUND)
            message_repeat_all = message_repeat_lfd + message_repeat_localstorage
            debug(message_repeat_all=message_repeat_all)
            # if STORAGE_FOUND:
            #     message_repeat_all = message_repeat_all + message_repeat_localstorage
            #     debug(message_repeat_all)
            # if LFD_FOUND:
            #     message_repeat_all = message_repeat_all + message_repeat_lfd
            #     debug(message_repeat_all)
            if message_repeat_all:
                self._set_headers()
                message = self._message_pack(find_name, repeat=message_repeat_all)
                debug(message=message)
                self.wfile.write(message)
            else:
                self.send_response(400)

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
    global config
    global SCAN_FINISHED
    global MAXVAL
    global EVENT
    global WIDGETS
    global PBAR
    # PBAR.start()
    TOTAL = 0
    n_progress = 1
    pool = ThreadPool(processes= 1)

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
    # lfd_class = lfd()
    # print "running monitoring repo dir 1"
    path = config.read_config('PACKAGES', 'dir')
    timeout = config.read_config('SCANNER', 'timeout', value=1)
    
    if timeout:
        timeout = int(timeout)
    else:
        timeout = 1
    # print("PATH =",path)
    debug(PATH=path)
    TOTAL = folder_size()
    config.write_config('PACKAGES', 'total', value=TOTAL)
    debug(TOTAL=TOTAL)
    
    while 1:
        if path and SCAN_FINISHED:
            total1 = folder_size()
            if not total1 == TOTAL and SCAN_FINISHED:
                # print "REPO CHANGED !"
                PBAR.start()
                sendnotify("REPO CHANGED !", 'Monitoring')
                debug("REPO CHANGED !", 'white', 'red')
                TOTAL = total1
                config.write_config('PACKAGES', 'total', value=TOTAL)
                try:
                    SCAN_FINISHED = False
                    lfd_class = lfd()
                    tx = pool.apply_async(lfd_class.parser_content, ())
                    while 1:
                        if not tx.get():
                            SCAN_FINISHED = False
                            # progressbar(1)
                            EVENT = "UPDATE REPO CHANGED"
                            if not n_progress == 100:
                                PBAR.update(n_progress)
                                n_progress += 1
                            else:
                                PBAR.update(0)
                                n_progress = 1
                        else:
                            PACKAGE_LOCALSTORAGE = tx.get()
                            SCAN_FINISHED = True
                            PBAR.finish()
                            break
                    # PACKAGE_LOCALSTORAGE = lfd_class.identify_localstorage(path)
                    
                    # print "SUCCESS UPDATE REPO !"
                    sendnotify("SUCCESS UPDATE REPO !", 'Update')
                    debug("SUCCESS UPDATE REPO !", 'white', 'red')
                except:
                    PBAR.finish()
                    traceback.format_exc()
                path = config.read_config('PACKAGES', 'dir')
                # print("PATH =",path)
                debug(PATH=path)
                timeout = config.read_config('SCANNER', 'timeout', value=1)
                
                if timeout:
                    timeout = int(timeout)
                else:
                    timeout = 1
                time.sleep(timeout)
            else:
                # print "monitoring ..."
                path = config.read_config('PACKAGES', 'dir')
                timeout = config.read_config('SCANNER', 'timeout', value=1)
                
                if timeout:
                    timeout = int(timeout)
                else:
                    timeout = 1
                time.sleep(timeout)
        else:
            # print "still scanning ..."
            # progressbar(1)
            path = config.read_config('PACKAGES', 'dir')
            # print("PATH =",path)
            debug(PATH=path)
            timeout = config.read_config('SCANNER', 'timeout', value=1)
            
            if timeout:
                timeout = int(timeout)
            else:
                timeout = 1
            time.sleep(timeout)
        if os.getenv('LFD_STOP_UPDATE') == '1':
            break

def progressbar(value, isFinish=False):    
    # global PBAR
    MAXVAL=100
    EVENT="UPDATE REPO 1"
    WIDGETS = ['%s: '%(EVENT), Percentage(), ' | ', ETA(), ' | ', AbsoluteETA()]
    PBAR = ProgressBar(widgets=WIDGETS, maxval=MAXVAL).start()
    n_progress = 1
    while 1:
        if not SCAN_FINISHED:
            if not n_progress == 100:
                PBAR.update(n_progress)
                n_progress+=1                
            else:    
                PBAR.update(0)
                n_progress = 0

        else:
            PBAR.finish()
            break

def sendnotify(message, event='Control', title="FastPypi"):
    try:
        mclass = sendgrowl.growl()
        icon = os.path.join(os.path.dirname(__file__), 'notify.png')
        appname = 'FastPypi'
        mclass.publish(appname, event, title, message, iconpath=icon)
    except:
        traceback.format_exc()
        pass

def prepare():
    global PACKAGES
    global PACKAGE_LOCALSTORAGE
    global config
    global SCAN_FINISHED

    path = config.read_config('PACKAGES', 'dir')
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
    TOTAL = float(folder_size())
    TOTAL_CONFIG = float(config.read_config('PACKAGES', 'total', value='0'))

    
    lfd_class = lfd()
    
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes= 2)
    t1 = pool.apply_async(lfd_class.parser_content, ())
    while 1:
        if not t1.get():
            time.sleep(1)
        else:
            PACKAGES = t1.get()
            break

    if not TOTAL == TOTAL_CONFIG:
        if not PACKAGE_LOCALSTORAGE:
            t2 = pool.apply_async(lfd_class.identify_localstorage, ())
            while 1:
                if not t2.get():
                    time.sleep(1)
                else:
                    PACKAGE_LOCALSTORAGE = t2.get()
                    SCAN_FINISHED = True
                    if os.getenv('DEBUG_EXTRA'):
                        debug(PACKAGE_LOCALSTORAGE = PACKAGE_LOCALSTORAGE)
                    break

def run(server_class=HTTPServer, handler_class=S, port=80):
    
    try:
        server_address = ('', port)
        server_address_print = server_address
        if server_address[0] == '':
            server_address_print = ('0.0.0.0', server_address[1])
        # httpd = server_class(server_address, handler_class)
        httpd = ThreadedHTTPServer(server_address, handler_class)
        # PBAR.start()
        if not vping.vping('8.8.8.8'):
            # print make_colors('NO INTERNET CONNECTION, SERVER WILL RUNNING AS LOCAL PYPI !', 'white', 'red', attrs=['blink'])
            print 'NO INTERNET CONNECTION, SERVER WILL RUNNING AS LOCAL PYPI !'
            
        print "Server Bind %s:%s" % server_address_print
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit('Server shutdown ...')
    except:
        traceback.format_exc()

def main(port=80):
    print 'Starting httpd ...'
    global MAXVAL
    global EVENT
    global WIDGETS
    global PBAR
    global SCAN_FINISHED
    n_progress = 1
    # PBAR = ProgressBar(widgets=WIDGETS, maxval=MAXVAL).start()
    PBAR.start()
    from threading import Thread
    # from multiprocessing.pool import ThreadPool
    # pool = ThreadPool(processes= 1)
    # t1 = pool.apply_async(prepare, ())
    # t3 = pool.apply_async(monitor_repo_dir, ())
    a = Thread(target=prepare)
    a.start()
    
    while 1:
        # print "SCAN_FINISHED =", SCAN_FINISHED
        if not SCAN_FINISHED:
        # if a.is_alive():
            if not n_progress == 100:
                PBAR.update(n_progress)
                n_progress += 1
                time.sleep(0.5)
            else:
                PBAR.update(0)
                n_progress = 1
        else:
            PBAR.finish()
            pool = ThreadPool(processes= 1)
            t1 = pool.apply_async(monitor_repo_dir, ())
            run(port=port)
            break
    
if __name__ == "__main__":
    print "PID:", PID
    from sys import argv

    if len(argv) == 2:
        # run(port=int(argv[1]))
        main(port=int(argv[1]))
    else:
        # run()
        main()
    
    #path = r'D:\PROJECTS\python-mpd2\apps\python-mpd2'
    #monitor_repo_dir(path)
    # global PBAR
    # PBAR.start()
    # for i in range(100):
    #     progressbar(i)
