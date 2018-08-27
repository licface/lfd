import convert

__TABLES__ = ['packages', 'localstorage']

class database(object):
    def __init__(self, host = None, port = None, username = None, password = None, dbname = None, table = None, dbtype = None):
        super(database, self)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname
        self.table = table
        self.dbtype = dbtype
        self.conn = None
        self.cursor = None
        self.SQL_CREATE = None
        self.SQL_CREATE_REPO = None
        
    
    def create(self):
        self.cursor.execute(self.SQL_CREATE)
        self.conn.commit()
        cursor.execute(self.SQL_CREATE_REPO)
        conn.commit()
        
    def get(self, table_name):
        exc01 = self.cursor.execute('SELECT * FROM %s;'%(table_name))
        self.conn.commit()
        return exc01.fetchall()
    
    def insert(self, datas=None, type = 'storage'):
        #type: database | storage
        if datas:
            SQL_INSERT = 'INSERT INTO packages (\'name\', \'description\', \'relpath\') VALUES("%s", "%s", "%s");' % (
                    datas[0], convert.convert(datas[1]), convert.convert(datas[2]))
            SQL_INSERT_LOCALSTORAGE = 'INSERT INTO localstorage (\'total\', \'packages\') VALUES("%s", "%s");' % (
                           datas[0], convert.convert(datas[1]))
            try:
                # print "SQL_INSERT =", SQL_INSERT
                if type == 'storage':
                    self.cursor.execute(SQL_INSERT_LOCALSTORAGE)	
                elif type == 'database':
                    self.cursor.execute(SQL_INSERT)
                self.conn.commit()
            except:
                if type == 'database':
                    SQL_INSERT = "INSERT INTO packages ('name', 'relpath') VALUES('%s', '%s');" % (datas[0], convert.convert(datas[2]))
                self.cursor.execute(SQL_INSERT)
                self.conn.commit()
                
    def truncate(self, table_name = 'all'):
        if not table_name == 'all':
            self.cursor.execute('DELETE FROM %s;'%(table_name))
            self.conn.commit()
            self.cursor.execute('VACUUM;')
            self.conn.commit()
        else:
            for i in __TABLES__:
                self.cursor.execute('DELETE FROM %s;'%(i))
                self.conn.commit()
                self.cursor.execute('VACUUM;')
                self.conn.commit()                
        
    def drop(self, table_name = 'all'):
        if not table_name == 'all':
            SQL_DROP = "DROP TABLE %s;" % (table_name)
            self.cursor.execute(SQL_DROP)
            self.conn.commit()
        else:
            for i in __TABLES__:
                SQL_DROP = "DROP TABLE %s;" % (i)
                self.cursor.execute(SQL_DROP)
                self.conn.commit()                    
        
    def setup(self, type='storage'):
        #type: storage | database
        config = configset.configset()
        config.configname = 'lfd.ini'
        dbname = self.dbname
        host = self.host
        port = self.port
        username = self.username
        password = self.password
        dbtype = self.dbtype
        if not dbname:
            dbname = config.read_config('DATABASE', 'name', value='lfd.db3')
        if not host:
            host = config.read_config('DATABASE', 'host', value='127.0.0.1')
        if not port:
            port = config.read_config('DATABASE', 'port', value='3306')
        if not dbtype:
            dbtype = config.read_config('DATABASE', 'type', value='sqlite')
        if not username:
            username = config.read_config('DATABASE', 'username', value='root')
        if not password:
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
            self.SQL_CREATE = SQL_CREATE
            self.SQL_CREATE_REPO = SQL_CREATE_REPO 
            
            conn = sqlite.connect(dbname)
            self.conn = conn
            cursor = conn.cursor()
            self.cursor = cursor
    
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