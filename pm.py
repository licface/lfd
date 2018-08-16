import os
import traceback
import sys
import tarfile
import zipfile
import shutil
import argparse
import time
import send2trash
import thread
from make_colors import make_colors
import easygui
from debug import debug
# debug = debugger.debug

class pm(object):
    def __init__(self, MASTER_PATH = None):
        super(pm, self)
        self.MASTER_PATH = MASTER_PATH
        #debug(self_MASTER_PATH_0 = self.MASTER_PATH)

    def translate(self, name):
        if str(name).endswith('.gz') or str(name).endswith('.zip') or str(name).endswith('.exe') or str(name).endswith('.msi') or str(name).endswith('.rar') or str(name).endswith('.whl') or str(name).endswith('.egg') or str(name).endswith('.bz2') or str(name).endswith('.tgz'):
            basename = os.path.basename(name)
            n = 2
            if "-" in name:
                len_basedname = len(str(name).split("-"))
                #print "len_basedname =", len_basedname
                basedname = str(basename).split("-",1)
                #print "basedname 0 =", basedname
                while 1:
                    if n <= len_basedname:
                        if basedname[n-1][0] == '' or basedname[n-1][0] == ' ':
                            break
                        else:
                            if not str(basedname[n-1][0]).isdigit():
                                #print "str(basedname[1][0]) =", str(basedname[1][0])
                                basedname = str(basename).split("-", n)
                                #print "basedname 1 =", basedname
                                n += 1
                            else:
                                if n == len_basedname:
                                    break
                                break
                    else:
                        break
                #print "basedname 0 =", basedname
                #print "n =", n
                #print '"-".join(basedname[0:n-1]).strip() =', "-".join(basedname[0:n-1]).strip()
                #print "-" * 200
                #print "name   =", name
                #print "join 0 =", "-".join(basedname[0:n-1]).strip()
                if os.path.basename(name) == "-".join(basedname[0:n-1]).strip():
                    basedname = str(name).split("-", 1)
                    #print "basedname 0 =", basedname
                    return basedname[0]
                else:
                    #print "basedname 1 =", basedname
                    return "-".join(basedname[0:n-1]).strip()
            else:
                if "." in name:
                    basedname = str(basename).split(".",1)
                    return basedname[0].strip()
                else:
                    if " " in name:
                        basedname = str(basename).split(" ",1)
                        return basedname[0].strip()
        return False

    def check_archive(self, name):
        if str(name).endswith(".gz"):
            try:
                tarname = tarfile.open(name)
                return True
            except:
                return False
        if str(name).endswith(".zip"):
            try:
                zipname = zipfile.ZipFile(name)
                testzip = zipname.testzip()
                if testzip == None:
                    return True
                else:
                    return False
            except:
                print "ERROR:",
                print traceback.format_exc()
                return False

    def moved(self, dirpath, path=None, overwrite=None, quiet=None, masterpath=None, noclean=None, verbosity = False, backup = False, simulate = False):
        filename = os.listdir(dirpath)
        if backup and not simulate:
            BACKUP_PATH = os.path.join(self.MASTER_PATH, "BACKUP")
            if not os.path.isdir(BACKUP_PATH):
                os.makedirs(BACKUP_PATH)
        is_overwrite = False
        if masterpath != None:
            self.MASTER_PATH = masterpath
        else:
            self.MASTER_PATH = self.MASTER_PATH
        for i in filename:
            i = os.path.join(self.MASTER_PATH, i)
            #print "i =", i
            if os.path.isfile(i):
                #print "translate =", self.translate(i)
                #print "-" * 200
                if not self.translate(i):
                    pass
                else:
                    M_PATH = os.path.join(self.MASTER_PATH, self.translate(i))
                    DEST_NAME = os.path.join(M_PATH, os.path.basename(i))
                    if path:
                        if not os.path.isdir(path) and not simulate:
                            os.makedirs(path)
                            M_PATH = path
                    if not os.path.isdir(M_PATH) and not simulate:
                        try:
                            os.makedirs(M_PATH)
                        except:
                            pass
                    #print "DEST_NAME =", DEST_NAME
                    #print "M_PATH =", M_PATH
                    #print "i =", i
                    if verbosity:
                        if overwrite:
                            if backup:
                                print make_colors('COPY', 'white', 'blue') + " " + make_colors("[OVERWRITE-BACKUP]", 'white', 'red') + ": " + make_colors(str(i), 'yellow') + make_colors(" --> ", 'green') + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[0], 'blue') + "\\" + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[1], 'cyan') + "\\" + make_colors(os.path.split(DEST_NAME)[1], 'magenta')
                            else:
                                print make_colors('COPY', 'white', 'blue') + " " + make_colors("[OVERWRITE]", 'white', 'red') + ": " + make_colors(str(i), 'yellow') + make_colors(" --> ", 'green') + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[0], 'blue') + "\\" + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[1], 'cyan') + "\\" + make_colors(os.path.split(DEST_NAME)[1], 'magenta')
                        else:
                            if backup:
                                print make_colors('COPY', 'white', 'blue') + " " + make_colors("[BACKUP]", 'white', 'red') + ": " + make_colors(str(i), 'yellow') + make_colors(" --> ", 'green') + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[0], 'blue') + "\\" + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[1], 'cyan') + "\\" + make_colors(os.path.split(DEST_NAME)[1], 'magenta')
                            else:
                                print make_colors('COPY', 'white', 'blue') + ": " + make_colors(str(i), 'yellow') + make_colors(" --> ", 'green') + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[0], 'blue') + "\\" + make_colors(os.path.split(os.path.split(DEST_NAME)[0])[1], 'cyan') + "\\" + make_colors(os.path.split(DEST_NAME)[1], 'magenta')
                    if overwrite and not simulate:
                        if os.path.isfile(DEST_NAME):
                            os.remove(DEST_NAME)
                        shutil.copy2(i, DEST_NAME)
                        #os.system('copy /y "%s" "%s >NUL"' % (i, DEST_NAME))
                    else:
                        if os.path.isfile(DEST_NAME):
                            if quiet and not simulate:
                                os.remove(DEST_NAME)
                                #os.system('copy /y "%s" "%s >NUL"' % (i, DEST_NAME))
                                shutil.copy2(i, DEST_NAME)
                            else:
                                if not overwrite:
                                    q =  raw_input(" Overwrite %s ? (y/n): " % make_colors(DEST_NAME, 'white', 'blue'))
                                    if str(q).lower() == 'y' or str(q).lower() == 'yes':
                                        if not simulate:
                                            os.remove(DEST_NAME)
                                        #os.system('copy /y "%s" "%s >NUL"' % (i, DEST_NAME))
                                        shutil.copy2(i, DEST_NAME)
                                    elif str(q).lower() == 'a' or str(q).lower() == 'all':
                                        quiet = True
                                else:
                                    if not simulate:
                                        os.remove(DEST_NAME)
                                    shutil.copy2(i, DEST_NAME)
                        else:
                            #os.system('copy "%s" "%s >NUL"' % (i, DEST_NAME))
                            if not simulate:
                                shutil.copy2(i, DEST_NAME)
                    #  thread.start_new(shutil.copy2, (i, DEST_NAME))
                    #shutil.copy2(i, DEST_NAME)
                    #os.system("move")
                    if not noclean:
                        if backup and not simulate:
                            shutil.move(i, BACKUP_PATH)
                            #os.system('move /y "%s" "%s"' % (i, BACKUP_PATH))
                        else:
                            #time.sleep(1)
                            if not simulate:
                                send2trash.send2trash(i)
            
    def usage(self):
        parser = argparse.ArgumentParser(formatter_class= argparse.RawTextHelpFormatter, description= 'Manage all file of python modules or packages in spesific folder')
        parser.add_argument('-o', '--overwrite', help='Overwrite File move to', action='store_true')
        parser.add_argument('-d', '--destination', help='Destination Folder default: MASTER_PATH with defintion or environment', action='store')
        parser.add_argument('-n', '--noclean', help='Dont delete source file', action='store_true')
        parser.add_argument('-q', '--quiet', help='No Supress', action='store_true')
        parser.add_argument('-v', '--verbosity', help='Show running process', action='store_true')
        parser.add_argument('-b', '--backup', help='Move to backup folder after copy', action='store_true')
        parser.add_argument('-t', '--test-simulate', help='Simulate process', action='store_true')
        
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            if args.destination:
                self.MASTER_PATH = args.destination
            if os.getenv("MASTER_PATH") != None:
                self.MASTER_PATH = os.getenv("MASTER_PATH")
            if not os.path.isdir(self.MASTER_PATH):
                q1 = raw_input('Root Directory [b = browser]: ')
                if q1 == 'b':
                    self.MASTER_PATH = easygui.diropenbox('Select Directory', 'MASTER_PATH', 'c:\\')
                else:
                    self.MASTER_PATH = q1
            if not os.path.isdir(self.MASTER_PATH):
                print make_colors('MASTER_PATH not Found !!!', 'white', 'red', ['bold', 'blink'])
                parser.print_help()
                sys.exit()
            print "MASTER_PATH =", make_colors(self.MASTER_PATH, 'white', 'red')
            self.moved(self.MASTER_PATH, self.MASTER_PATH, args.overwrite, args.quiet, self.MASTER_PATH, args.noclean, args.verbosity, args.backup, args.test_simulate)

if __name__ == "__main__":
    #print translate(sys.argv[1])
    #check_archive(sys.argv[1])
    #data = sys.argv[1:len(sys.argv)]
    c = pm()
    c.usage()
