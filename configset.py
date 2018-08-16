import sys
import argparse
import ConfigParser
import os
import traceback
import re
from collections import OrderedDict
from debug import * 
from make_colors import make_colors

__sdk__ = '2.7'
__platform__ = 'all'
__url__ = 'licface@yahoo.com'
__build__ = '2.7'

configname ='conf.ini'

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)


class configset(object):
    cfg = ConfigParser.RawConfigParser(allow_no_value=True)
    cfg.optionxform = str
    THIS_PATH = os.path.dirname(__file__)
    # configname ='conf.ini'
    # debug(configname = configname)
    
    def __init__(self):
        super(configset, self)
        global configname
        self.configname = configname
    
    def get_config_file(self, filename='', verbosity=None):
        if not filename:
            filename = self.configname
        configname = filename
        self.configname = configname
        debug(configname = filename)
        self.configname = configname
        debug(configset_configname = self.configname)
        
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            debug(checking_001 = "os.path.isfile(os.path.join(os.getcwd(), filename))")
            self.configname =os.path.join(os.getcwd(), filename)
            debug(configname = os.path.join(os.getcwd(), filename))
            return os.path.join(os.getcwd(), filename)
        elif os.path.isfile(filename):
            debug(checking_002 = "os.path.isfile(filename)")
            self.configname =filename
            debug(configname = os.path.abspath(filename))
            return filename
        elif os.path.isfile(os.path.join(os.path.dirname(__file__), filename)):
            debug(checking_003 = "os.path.isfile(os.path.join(os.path.dirname(__file__), filename))")
            self.configname =os.path.join(os.path.dirname(__file__), filename)
            debug(configname = os.path.join(os.path.dirname(__file__), filename))
            return os.path.join(os.path.dirname(__file__), filename)
        elif os.path.isfile(self.configname):
            debug(checking_004 = "os.path.isfile(configname)")
            debug(configname = os.path.abspath(configname))
            return configname
        elif os.path.isfile(os.path.join(os.path.dirname(__file__), self.configname)):
            debug(checking_005 = "os.path.isfile(os.path.join(os.path.dirname(__file__), configname))")
            debug(configname = os.path.join(os.path.dirname(__file__), self.configname))
            return os.path.join(os.path.dirname(__file__), self.configname)
        else:
            debug(checking_006 = "ELSE")
            fcfg = self.configname
            f = open(fcfg, 'w')
            f.close()
            filecfg = fcfg
            debug(CREATE = os.path.abspath(filecfg))
            return filecfg
    
    def write_config(self, section, option, filename='', value=None, cfg = None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        #cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict)
        #debug(filename = filename)
        debug(value = value)
        if cfg:
            debug(cfg_not_none = True)
            configset.cfg.read(filename)
        #if not value == None:
        #if os.path.isfile(os.path.join(THIS_PATH, filename)):
            #configset.cfg.read(filename)
        #else:
            #filename = self.get_config_file()
            #configset.cfg.read(filename)
        try:
            debug(cfg_set = True)
            configset.cfg.set(section, option, value)
        except ConfigParser.NoSectionError:
            debug(cfg_add = True)
            configset.cfg.add_section(section)
            configset.cfg.set(section, option, value)
        cfg_data = open(filename,'wb')
        configset.cfg.write(cfg_data) 
        cfg_data.close()  
        
        return self.read_config(section, option, filename)
        
    def write_config2(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        #cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        if not value == None:
            if os.path.isfile(os.path.join(THIS_PATH, filename)):
                configset.cfg.read(filename)
            else:
                filename = self.get_config_file()
                configset.cfg.read(filename)
            try:
                configset.cfg.get(section, option)
                configset.cfg.set(section, option, value)
            except ConfigParser.NoSectionError:
                #configset.cfg.add_section(section)
                #configset.cfg.set(section, option, value)
                return "\tNo Section Name: '%s'" %(section)
            except ConfigParser.NoOptionError:
                return "\tNo Option Name: '%s'" %(option)
            cfg_data = open(filename,'wb')
            configset.cfg.write(cfg_data)   
            cfg_data.close()
            return ''
        else:
            return "No Value set !"
        
    def read_config(self, section, option, filename='', value=None, verbosity=None):
        """
            option: section, option, filename='', value=None
        """
        filecfg = self.get_config_file(filename, verbosity)
        configset.cfg.read(filecfg)
        
        # debug(section = section)
        # debug(option = option)
        # debug(value = value)
        # debug(filecfg = str(filecfg))
        # debug(filecfg = os.path.abspath(str(filecfg)))
        
        try:
            data = configset.cfg.get(section, option)
        except:
            try:
                self.write_config(section, option, filename, value)
            except:
                traceback.format_exc()
            data = configset.cfg.get(section, option)
        return data
        
    def read_config2(self, section, option, filename='', verbosity=None): #format ['aaa','bbb','ccc','ddd']
        """
            option: section, option, filename=''
            format result: ['aaa','bbb','ccc','ddd']
            
        """
        filename = self.get_config_file(filename, verbosity)
        cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        cfg.read(filename)
        cfg = cfg.get(section, option)
        return cfg
    
    def read_config3(self, section, option, filename='', verbosity=None): #format result: [[aaa.bbb.ccc.ddd, eee.fff.ggg.hhh], qqq.xxx.yyy.zzz]
        """
            option: section, option, filename=''
            format result: [[aaa.bbb.ccc.ddd, eee.fff.ggg.hhh], qqq.xxx.yyy.zzz]
            
        """
        filename = self.get_config_file(filename, verbosity)
        data = []
        cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        cfg.read(filename)
        cfg = cfg.get(section, option)
        for i in cfg:
            if "," in i:
                d1 = str(i).split(",")
                d2 = []
                for j in d1:
                    d2.append(str(j).strip())
                data.append(d2)
            else:
                data.append(i)
        return data
    
    def read_config4(self, section, option, filename='', value = '', verbosity=None): #format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
        """
            option: section, option, filename=''
            format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
            
        """
        filename = self.get_config_file(filename, verbosity)
        debug(filename = filename)
        data = []
        cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict)
        #print "CFG =", cfg
        cfg.read(filename)
        debug(cfg0 = cfg)
        try:
            cfg = cfg.get(section, option)
            debug(cfg1 = cfg)
            if not cfg == None:
                for i in cfg:
                    if "," in i:
                        d1 = str(i).split(",")
                        for j in d1:
                            data.append(str(j).strip())
                    else:
                        data.append(i)
                return data
            else:
                return None
        except:
            debug(ERROR = traceback.format_exc())
            debug(except_has = True)
            data = self.write_config(section, option, filename, value, cfg)
            debug(data = data)
            return data
    
    def read_config5(self, section, option, filename='', verbosity=None): #format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}
        """
            option: section, option, filename=''
            format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}
            
        """
        filename = self.get_config_file(filename, verbosity)
        data = {}
        cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        configset.cfg.read(filename)
        cfg = configset.cfg.get(section, option)
        for i in cfg:
            if "," in i:
                d1 = str(i).split(",")
                for j in d1:
                    d2 = str(j).split(":")
                    data.update({str(d2[0]).strip():int(str(d2[1]).strip())})
            else:
                for x in i:
                    e1 = str(i).split(":")
                    data.update({str(e1[0]).strip():int(str(e1[1]).strip())})
        return data
    
    def read_config6(self, section, option, filename='', verbosity=None): #format result: {aaa:[bbb, ccc], ddd:[eee, fff], ggg:[hhh, qqq], xxx:[yyy:zzz]}
        """
            
            option: section, option, filename=''
            format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}
            
        """
        filename = self.get_config_file(filename, verbosity)
        data = {}
        cfg = ConfigParser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        configset.cfg.read(filename)
        cfg = configset.cfg.get(section, option)
        for i in cfg:
            if ":" in i:
                d1 = str(i).split(":")
                d2 = int(str(d1[0]).strip())
                for j in d1[1]:
                    d3 = re.split("['|','|']", d1[1])
                    d4 = str(d3[1]).strip()
                    d5 = str(d3[-2]).strip()
                    data.update({d2:[d4, d5]})
            else:
                pass    
        return data
        
    def get_config(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config(section, option, filename, value)
        except ConfigParser.NoSectionError:
            print traceback.format_exc()
            self.write_config(section, option, filename, value)
            data = self.read_config(section, option, filename, value)
        except ConfigParser.NoOptionError:
            print traceback.format_exc()
            self.write_config(section, option, filename, value)
            data = self.read_config(section, option, filename, value)
        return data
    
    def get_config2(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config2(section, option, filename)
        except ConfigParser.NoSectionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config2(section, option, filename)
        except ConfigParser.NoOptionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config2(section, option, filename)
        return data
    
    def get_config3(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config3(section, option, filename)
        except ConfigParser.NoSectionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config3(section, option, filename)
        except ConfigParser.NoOptionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config3(section, option, filename)
        return data
    
    def get_config4(self, section, option, filename='', value='', verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config4(section, option, filename)
        except ConfigParser.NoSectionError:
            #print "Error 1 =", traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config4(section, option, filename)
            #print "data 1 =", data
        except ConfigParser.NoOptionError:
            #print "Error 2 =", traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config4(section, option, filename)
            #print "data 2 =", data
        #print "DATA =", data
        return data
    
    def get_config5(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config5(section, option, filename)
        except ConfigParser.NoSectionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config5(section, option, filename)
        except ConfigParser.NoOptionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config5(section, option, filename)
        return data
    
    def get_config6(self, section, option, filename='', value=None, verbosity=None):
        filename = self.get_config_file(filename, verbosity)
        try:
            data = self.read_config6(section, option, filename)
        except ConfigParser.NoSectionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config6(section, option, filename)
        except ConfigParser.NoOptionError:
            print traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config6(section, option, filename)
        return data
    
    def write_all_config(self, filename='', verbosity=None):
        filename = self.get_config_file(filename, verbosity)
    
    def read_all_config(self, filename='', section=[], verbosity=None):
        filecfg = self.get_config_file(filename, verbosity)
        configset.cfg.read(filecfg)    
        data = {}
        dbank = []
        if len(section) != 0:
            for x in configset.cfg.options(section):
                d = configset.cfg.get(section, x)
                data.update({x:d})
            dbank.append([section,data])        
        else:    
            #print "configset.cfg.sections() =", configset.cfg.sections()
            for i in configset.cfg.sections():
                section.append(i)
                for x in configset.cfg.options(i):
                    d = configset.cfg.get(i, x)
                    data.update({x:d})
                dbank.append([i,data])
        #print "dbank =",  dbank
        return dbank
        
    def read_all_section(self, filename='', section='server', verbosity=None):
        filecfg = self.get_config_file(filename, verbosity)
        configset.cfg.read(filecfg)    
        dbank = []
        dhost = []
        for x in configset.cfg.options(section):
            d = configset.cfg.get(section, x)
            #data.update({x:d})
            dbank.append(d)
            if d:
                if ":" in d:
                    data = str(d).split(":")
                    host = str(data[0]).strip()
                    port = int(str(data[1]).strip())
                    dhost.append([host,  port])
        #print "dbank =",  dbank
        #print "dhost =",  dhost
        return [dhost,  dbank]
            
    def test(verbosity=None):
        filename = self.get_config_file(verbosity)
        configset.cfg.read(filename)
        data = configset.cfg.sections()
        print configset.cfg.get('router','host')
        print data
    def usage(self):
        parser = argparse.ArgumentParser(formatter_class= argparse.RawTextHelpFormatter)
        parser.add_argument('CONFIG_FILE', action = 'store', help = 'Config file name path')
        parser.add_argument('-r', '--read', help = 'Read Action', action = 'store_true')
        parser.add_argument('-w', '--write', help = 'Write Action', action = 'store_true')
        parser.add_argument('-s', '--section', help = 'Section Write/Read', action = 'store')
        parser.add_argument('-o', '--option', help = 'Option Write/Read', action = 'store')
        parser.add_argument('-t', '--type', help = 'Type Write/Read', action = 'store', default = 1, type = int)
        if len(sys.argv) == 1:
            print "\n"
            parser.print_help()
        else:
            print "\n"
            args = parser.parse_args()
            if args.CONFIG_FILE:
                self.configname =args.CONFIG_FILE
                if args.read:
                    if args.type == 1:
                        if args.section and args.option:
                            self.read_config(args.section, args.option)
                    elif args.type == 2:
                        if args.section and args.option:
                            self.read_config2(args.section, args.option)
                    elif args.type == 3:
                        if args.section and args.option:
                            self.read_config3(args.section, args.option)
                    elif args.type == 4:
                        if args.section and args.option:
                            self.read_config4(args.section, args.option)
                    elif args.type == 5:
                        if args.section and args.option:
                            self.read_config5(args.section, args.option)
                    elif args.type == 6:
                        if args.section and args.option:
                            self.read_config6(args.section, args.option)
                    else:
                        print make_colors("INVALID TYPE !", 'white', 'red', ['blink'])
                        print "\n"
                        parser.print_help()
                else:
                    print make_colors("Please use '-r' for read or '-w' for write", 'white', 'red', ['blink'])
                    print "\n"
                    parser.print_help()
            else:
                print make_colors("NO FILE CONFIG !", 'white', 'red', ['blink'])
                print "\n"
                parser.print_help()
    
configset_class = configset()
get_config_file = configset_class.get_config_file
write_config = configset_class.write_config
write_config2 = configset_class.write_config2
read_config = configset_class.read_config
read_config2 = configset_class.read_config2
read_config3 = configset_class.read_config3
read_config4 = configset_class.read_config4
read_config5 = configset_class.read_config5
read_config6 = configset_class.read_config6
get_config = configset_class.get_config
get_config2 = configset_class.get_config2
get_config3 = configset_class.get_config3
get_config4 = configset_class.get_config4
get_config5 = configset_class.get_config5
get_config6 = configset_class.get_config6
write_all_config = configset_class.write_all_config
read_all_config = configset_class.read_all_config
read_all_section = configset_class.read_all_section
test = configset_class.test
usage = configset_class.usage

if __name__ == '__main__':
    usage()