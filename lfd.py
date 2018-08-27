import os
import sys
import requests
from bs4 import BeautifulSoup as bs
import argparse
import configset
import parserheader
import re
import codecs
import pm
import tarfile
import zipfile
import convert
from debug import debug
PID = os.getpid()
import cmdw
MAX_WIDTH = cmdw.getWidth()
TEST_COUNT = 0


class lfd(object):

    def __init__(self):
        super(lfd, self)
        self.URL = 'https://www.lfd.uci.edu/~gohlke/pythonlibs/'
        self.URL_DOWNLOAD = 'https://download.lfd.uci.edu/pythonlibs/'
        self.INDEX = "l8ulg3xw"
        self.CONFIG_NAME = 'lfd.ini'
        self.SESS = requests.Session()
        # self.PACKAGES = self.parser_content()
        self.pm = pm.pm

    def config(self, section, option, value=None, configname=None):
        if configname:
            self.CONFIG_NAME = configname
        conf = configset.configset()
        conf.configname = self.CONFIG_NAME
        if value:
            configset.write_config(section, option, value)
        return configset.read_config(section, option)

    def minusreplace(self, exc):
        if exc.object[exc.start:exc.end] == u'\u2011':
            return (u'-', exc.end)
        return (u'?', exc.end)

    def parser_content(self):
        global TEST_COUNT
        codecs.register_error('minusreplace', self.minusreplace)
        req = self.SESS.get(self.URL)
        content = ''
        package_dict = {}

        if req.ok:
            content = req.content
            b = bs(content, 'lxml')
            a = b.find('ul', {'class': 'pylibs'})
            all_group_packages = a.find_all_next('ul')
            all_group_packages_main = a.find_all_next('ul')[0:-1]
            # print all_group_packages_main[0]
            all_strong_package_name = a.find_all_next('strong')[0:-6]
            # print "all_strong_package_name[-2] =",all_strong_package_name[-2]
            # print "all_strong_package_name[-1] =",all_strong_package_name[-1]
            # print "parent"
            # print all_strong_package_name[-1].parent
            # print "+"*MAX_WIDTH
            # print all_group_packages_main[-1]

            # sys.exit(0)
            n = 1
            for i in all_group_packages_main:
                index = all_group_packages_main.index(i)
                # print "index =", index
                # print "len(all_strong_package_name) =",
                # len(all_strong_package_name)
                m = 0
                package_name = all_strong_package_name[index].text
                if package_name == u'Misc':
                    package_desc = "Misc Packages"
                # print "package_name =", package_name
                else:
                    package_desc = " ".join(unicode(all_strong_package_name[
                        index].parent.text.strip()).encode('utf-8').split('\n\n')[0].split('\n'))
                # print "package_desc =", package_desc

                all_a_per_group = all_group_packages_main[index].find_all('a')
                # print "all_a_per_group =", all_a_per_group
                # print "-" * MAX_WIDTH
                packages = {}
                for p in all_a_per_group:
                    name = p.text.encode('cp850', errors='minusreplace')
                    if name:
                        # print "name =", name
                        link = self.URL_DOWNLOAD + self.INDEX + "/" + name
                        # print "link =", link
                        packages.update({
                            m: {'name': name, 'link': link}
                        })
                    m += 1
            #  print packages
                # print "-" * MAX_WIDTH
                package_dict.update({
                    n: {
                        'package_name': str(package_name).lower(),
                        'package_desc': package_desc,
                        'packages': packages
                    }
                })
                n += 1
            # print "package_dict.keys() =",package_dict.keys()
            # print "package_dict:"
            # print package_dict
            # print package_dict.get(package_dict.keys()[0])
            # print "-" * MAX_WIDTH
            # print package_dict.get(package_dict.keys()[1])
            # print "-" * MAX_WIDTH
            # print package_dict.get(package_dict.keys()[2])
        return package_dict

        # else:
        #     return req.content

    def find(self, package_name, python_version, architecture, packages_db=None):
        architecture = architecture + ".whl"
        package_name = unicode(package_name).lower()
        package_name_alt = package_name.replace("-", "_")
        if packages_db:
            packages = packages_db
        else:
            packages = self.parser_content()
        # print packages
        # print "#" * MAX_WIDTH
        for i in packages:
            if packages.get(i).get('package_name') == package_name or packages.get(i).get('package_name') == package_name_alt:
                    # print "THE LINKS"
                find_packages = packages.get(i).get('packages')
                find_packages_name = packages.get(i).get('package_name')
                # print "find_packages =", find_packages
                if find_packages:
                    for p in find_packages:
                        pp = find_packages.get(p)
                        name = pp.get('name')
                        link = pp.get('link')
                        # print "name =", name
                        # print "link =", link
                        name_split = re.split('-', name)
                        # print "name_split =", name_split
                        if python_version in name_split:
                            # print "name_split FOUND:", name_split
                            if architecture in name_split:
                                print "FOUND LINK:", link
                                return link, name, find_packages_name
                else:
                    return '','',''

    def find_localstorage(python_version, architecture, packages_list):
        for i in packages_list:
            name = os.path.basename(i)
            name_split = re.split('-', name)
            if python_version in name_split:
                if architecture in name_split:
                    return i
        return ''

    def find_localstorage_basename(basename):
        for i in packages_list:
            name = os.path.basename(i)
            if name == basename:
                return i
        return ''

    def serve(self, host='0.0.0.0', port='7775'):
        pass

    def install(self, host='0.0.0.0', port='7775'):
        pass

    def usage(self):
        pass

    def get_readme(self, file, testzipfile=False):
        if str(file).endswith(".gz"):
            try:
                tar_file = tarfile.open(file)
                for i in tar_file.getnames():
                    if i.endswith('README.rst') or i.endswith('README.md') or i.endswith('README'):
                        f = tar_file.extractfile(i)
                        return f.read()
                return ''
            except:
                print traceback.format_exc()
                return False

        elif str(file).endswith(".zip"):
            try:
                zip_file = zipfile.ZipFile(file)

                if testzipfile:
                    testzip = zip_file.testzip()
                    if testzip == None:
                        pass
                    else:
                        return "zipfile corrupt !"
                for i in zip_file.namelist():
                    if i.endswith('README.rst') or i.endswith('README.md') or i.endswith('README'):
                        return zip_file.read(i)
                return ''
            except:
                print traceback.format_exc()
                return False

        elif str(file).endswith(".whl"):
            try:
                zip_file = zipfile.ZipFile(file)

                if testzipfile:
                    testzip = zip_file.testzip()
                    if testzip == None:
                        pass
                    else:
                        return "zipfile corrupt !"
                for i in zip_file.namelist():
                    if i.endswith('METADATA'):
                        return zip_file.read(i)
                return ''
            except:
                print traceback.format_exc()
                return False
        else:
            return ''

    def update_database(self, path=None):
        ######################################
        #          STILL ERROR               #
        ######################################
        config = configset.configset()
        config.configname = 'lfd.ini'
        path_name = path
        if os.getenv('PACKAGES_DIR'):
            path = os.getenv('PACKAGES_DIR')
        if config.read_config('PACKAGES', 'dir', value='.'):
            path = config.read_config('PACKAGES', 'dir', value='.')
        if path_name:
            path = path_name
        if path == ".":
            path = os.getcwd()
        packages = self.identify_localstorage(path)
        self.database().truncate('packages')
        self.database().truncate('localstorage')
        for i in packages:
            description = self.get_readme(packages.get(i)[0])
            self.database((i, description, packages.get(i))).insert()

    def get_name_localstorage(self, package):
        p = self.pm()
        package = os.path.basename(package)
        name = p.translate(package)
        if name:
            return name.lower()
        else:
            return ''

    def identify_localstorage(self, path=None):
        config = configset.configset()
        config.configname = 'lfd.ini'

        path_name = path
        if os.getenv('PACKAGES_DIR'):
            path = os.getenv('PACKAGES_DIR')
        if config.read_config('PACKAGES', 'dir', value='.'):
            path = config.read_config('PACKAGES', 'dir', value='.')
        # if path_name:
        #     path = path_name
        if path == ".":
            path = os.getcwd()
        if path == None:
            q = raw_input(
                'PATH IS NONE [EMPTY], DO YOU WANT TO CONTINUE WITH THIS CURRENT PATH [y/n]:')
            if q == 'y':
                path = os.getcwd()
            elif q == 'n':
                print make_colors("EXIT NO PATH", 'white', 'lightred', ['blink'])
                sys.exit('EXIT NO PATH')
            else:
                print make_colors("RETURN EMPTY DATA", 'white', 'lightred', ['blink'])
                return dir_dict

        dir_dict = {}
        MODE = config.read_config('SCANNER', 'mode', value='walk')

        def walk():
            for ROOT, DIRS, FILES in os.walk(path):
                if FILES:
                    for i in FILES:
                        name = self.get_name_localstorage(i)
                        if name:
                            if not dir_dict.get(name):
                                dir_dict.update({name: []})
                            dir_dict.get(name).append(os.path.join(ROOT, i))

        def win():
            if " " in path:
                path = '"%s"' % (path)
            pattern = "dir /s /b %s" % (path)
            listdir = os.popen(pattern).readlines()
            for i in listdir:
                i_name = os.path.basename(i)
                name = self.get_name_localstorage(i_name)
                if name:
                    if not dir_dict.get(name):
                        dir_dict.update({name: []})
                    dir_dict.get(name).append(i)

        if MODE == 'walk':
            walk()
        elif MODE == 'win':
            win()
        else:
            walk()
        return dir_dict

    def database(self, datas=None, type='storage', table_name = None):
        #type: storage | database
        config = configset.configset()
        config.configname = 'lfd.ini'
        dbname = config.read_config('DATABASE', 'name', value='lfd.db3')
        host = config.read_config('DATABASE', 'host', value='127.0.0.1')
        port = config.read_config('DATABASE', 'port', value='3306')
        dbtype = config.read_config('DATABASE', 'type', value='sqlite')
        username = config.read_config('DATABASE', 'username', value='root')
        password = config.read_config('DATABASE', 'password', value='')

        debug(dbname=dbname)
        debug(host=host)
        debug(port=port)
        debug(dbtype=dbtype)

        if dbtype == 'sqlite':
            try:
                # from sqlite3 import dbapi2 as sqlite
                import sqlite3 as sqlite
            except ImportError:
                sys.exit(
                    "You not have module \"pysqlite2\", please download before ! \n")
            except:
                traceback.format_exc()
                sys.exit("ERROR by SYSTEM")

            SQL_CREATE = '''CREATE TABLE IF NOT EXISTS packages ( \
                       'id' INTEGER PRIMARY KEY  AUTOINCREMENT, \
                       'name' VARCHAR(255) NOT NULL, \
                       'description' VARCHAR(255) NOT NULL, \
                       'relpath' VARCHAR(255) NOT NULL);'''
            SQL_CREATE_REPO = '''CREATE TABLE IF NOT EXISTS localstorage ( \
                       'total' VARCHAR(255) NOT NULL, \
                       'packages' VARCHAR(255) NOT NULL);'''
            SQL_DROP = "DROP TABLE %s;" % (table_name)
            conn = sqlite.connect(dbname)
            cursor = conn.cursor()
            def create():
                cursor.execute(SQL_CREATE)
                conn.commit()
                cursor.execute(SQL_CREATE_REPO)
                conn.commit()
            def get(table_name):
                exc01 = cursor.execute('SELECT * FROM %s;'%(table_name))
                conn.commit()
                return exc01.fetchall()
            def insert():
                if datas:
                    SQL_INSERT = 'INSERT INTO packages (\'name\', \'description\', \'relpath\') VALUES("%s", "%s", "%s");' % (
                            datas[0], convert.convert(datas[1]), convert.convert(datas[2]))
                    SQL_INSERT_LOCALSTORAGE = 'INSERT INTO localstorage (\'total\', \'packages\') VALUES("%s", "%s");' % (
                                   datas[0], convert.convert(datas[1]))
                    try:
                        # print "SQL_INSERT =", SQL_INSERT
                        if type == 'storage':
                            cursor.execute(SQL_INSERT_LOCALSTORAGE)	
                        elif type == 'database':
                            cursor.execute(SQL_INSERT)
                        conn.commit()
                    except:
                        if type == 'database':
                            SQL_INSERT = "INSERT INTO packages ('name', 'relpath') VALUES('%s', '%s');" % (datas[0], convert.convert(datas[2]))
                        cursor.execute(SQL_INSERT)
                        conn.commit()
            def truncate(table_name):
                cursor.execute('DELETE FROM %s;'%(table_name))
                conn.commit()
                cursor.execute('VACUUM;')
                conn.commit()
            def drop():
                cursor.execute(SQL_DROP)
                conn.commit()

        elif dbtype == 'mysql':
            SQL_CREATE = '''CREATE TABLE IF NOT EXISTS packages ( \
                       `id` BIGINT(100) AUTO_INCREMENT NOT NULL PRIMARY KEY, \
                       `name` VARCHAR(255) NOT NULL, \
                       `description` VARCHAR(255) NOT NULL, \
                       `relpath` VARCHAR(255) NOT NULL)'''

            try:
                import MySQLdb
                conn = MySQLdb.connect(
                    host, username, password, dbname, port)
                cursor = conn.cursor()
            except ImportError:
                sys.exit(
                    "You not have module \"MySQLdb\", please download before ! \n")
            except:
                try:
                    conn = MySQLdb.connect(
                        host, username, password, port=port)
                    cursor = conn.cursor()
                    cursor.execute(SQL_CREATE)
                    conn.commit()
                except:
                    traceback.format_exc()
                    sys.exit("ERROR by SYSTEM")
                if datas:
                    try:
                        SQL_INSERT = "INSERT INTO packages (`name`, `description`, `relpath`) VALUES(%s, %s, %s);" % (
                            datas[0], datas[1], datas[2])
                        cursor.execute(SQL_INSERT)
                        conn.commit()
                    except:
                        SQL_INSERT = "INSERT INTO packages (`name`, `description`, `relpath`) VALUES(%s, %s, %s);" % (
                            datas[0], ' ', datas[2])
                        cursor.execute(SQL_INSERT)
                        conn.commit()

        elif dbtype == 'oracle':
            SQL_CREATE = '''CREATE TABLE IF NOT EXISTS packages ( \
                       'id' BIGINT(100) GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) NOT NULL PRIMARY KEY, \
                       'name' VARCHAR(255) NOT NULL, \
                       'description' VARCHAR(255) NOT NULL, \
                       'relpath' VARCHAR(255) NOT NULL)'''
            sys.exit("STILL DEVELOPMENT, PLEASE USE ANOTHER DATABASE TYPE")

        elif dbtype == 'postgres':
            SQL_CREATE = '''CREATE TABLE IF NOT EXISTS packages ( \
                       'id' BIGSERIAL NOT NULL PRIMARY KEY, \
                       'name' VARCHAR(255) NOT NULL, \
                       'description' VARCHAR(255) NOT NULL, \
                       'relpath' VARCHAR(255) NOT NULL)'''

            try:
                import psycopg2
                conn = psycopg2.connect("dbname=%s, user=%s, password=%s, host=%s, port=%s" % (
                    dbname, username, password, host, port))
                cursor = conn.cursor()
                cursor.execute(SQL_CREATE)
                conn.commit()
            except ImportError:
                sys.exit(
                    "You not have module \"Psycopg2\", please download before ! \n")
            except:
                traceback.format_exc()
                sys.exit("ERROR by SYSTEM")


if __name__ == '__main__':
    print "PID:", PID
    c = lfd()
    c.find(sys.argv[1], 'cp27', 'win_amd64')
    # c.parser_content()
    # c.usage()
