#!/usr/bin/env python3

import os
import sys
import argparse

from utils import log
from ansible_autodoc.Config import SingleConfig
from ansible_autodoc.DocumentationParser import Parser


class AnsibleAutodoc:

    def __init__(self):
        self.config = SingleConfig()
        self.log = log.SingleLog(self.config.debug_level)
        self._args()

        doc = Parser()

    def _args(self):
        usage = '''TODO: add usage

        '''
        parser = argparse.ArgumentParser(description='Generate Ansible Documentation', usage=usage)
        # parser.add_argument("-f", "--force", help="Force online list", action="store_true")
        # parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag', required=True)
        # parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag')
        debug_level = parser.add_mutually_exclusive_group()
        debug_level.add_argument('-v', action='store_true', help='Set debug level to info')
        debug_level.add_argument('-vv', action='store_true', help='Set debug level to debug')
        debug_level.add_argument('-vvv', action='store_true', help='Set debug level to trace')

        parser.add_argument('dir', nargs='?', default=os.getcwd())
        parser.add_argument('-o', action="store", dest="out", type=str)

        args = parser.parse_args()

        self.config.base_dir = os.path.abspath(args.dir)

        if args.v is True:
            self.log.set_level("info")
        elif args.vv is True:
            self.log.set_level("debug")
        elif args.vvv is True:
            self.log.set_level("trace")
        else:
            self.log.set_level("warn")

        if args.out is None:
            self.config.output_dir = os.path.abspath(os.getcwd()+"/doc")
        else:
            self.config.output_dir = os.path.abspath(args.out)

        if os.path.isdir(self.config.base_dir+"/roles" ):
            self.config.is_role = False
        elif os.path.isdir(self.config.base_dir+"/tasks" ):
            self.config.is_role = True
            self.config.role_name = os.path.basename(self.config.base_dir)
        else:
            print("Error: I cloud not find a project nor a role to document: \n"
                  " I checked for: "+ self.config.base_dir+"/roles (project) \n"
                                                           " and:  "+ self.config.base_dir+"/tasks (role)" )
            sys.exit(1)

        self.log.debug(args)
        self.log.info("Using base dir: "+self.config.base_dir)
        self.log.info("Using output dir: "+self.config.output_dir)
        self.log.info("This is detected as a role: "+str(self.config.is_role))
