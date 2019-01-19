#!/usr/bin/python3
import pprint

from utils.singleton import Singleton


class Log:
    levels= {
        "trace":-1,
        "debug":0,
        "info":1,
        "warn":2,
        "error":3,
    }
    log_level= 1

    def __init__(self,level=1):
        self.set_level(level)

    def set_level(self,s):

        if isinstance(s, str):
            for level,v in self.levels.items():
                if level == s:
                    self.log_level = v
        elif isinstance(s, int):
            if s in range(4):
                self.log_level = s

    def trace(self,msg,h=""):
        if self.log_level <= -1:
            self._p("*TRACE*: "+h,msg)

    def debug(self,msg,h=""):
        if self.log_level <= 0:
            self._p("*DEBUG*: "+h,msg)

    def info(self,msg,h=""):
        if self.log_level <= 1:
            self._p("*INFO*: "+h,msg)

    def warn(self,msg,h=""):
        if self.log_level <= 2:
            self._p("*WARN*: "+h,msg)

    def error(self,msg,h=""):
        if self.log_level <= 3:
            self._p("*ERROR*: "+h,msg)

    def _p(self,head,msg):

        if isinstance(msg,list):
            print(head+" <list>")
            i=0
            for line in msg:
                print("  ["+str(i)+"]: "+str(line))
                i +=1

        elif isinstance(msg,dict):
            print(head+" <dict>")
            pprint.pprint(msg)
        else:
            print(head+str(msg))


class SingleLog(Log,metaclass=Singleton):
    pass
