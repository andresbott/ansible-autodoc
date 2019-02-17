#!/usr/bin/env python3

import os
import sys
import argparse

from ansibleautodoc.Utils import SingleLog
from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.DocumentationParser import Parser
from ansibleautodoc.DocumentationGenerator import Generator
from ansibleautodoc import __version__

class AnsibleAutodoc:

    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog(self.config.debug_level)
        args = self._cli_args()
        self._parse_args(args)

        doc_parser = Parser()
        doc_generator = Generator(doc_parser)
        doc_generator.render()


    def _cli_args(self):
        """
        use argparse for parsing CLI arguments
        :return: args objec
        """
        usage = '''ansible-autodoc [project_directory] [options]'''
        parser = argparse.ArgumentParser(description='Generate documentation from annotated playbooks and roles using templates', usage=usage)
        # parser.add_argument("-f", "--force", help="Force online list", action="store_true")
        # parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag', required=True)
        # parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag')

        parser.add_argument('project_dir', nargs='?', default=os.getcwd(),help="Project directory to scan, "
                                                                               "if empty current working will be used.")
        parser.add_argument('-C',"--conf", nargs='?', default="",help="specify an configuration file")
        parser.add_argument('-o', action="store", dest="output", type=str, help='Define the destination '
                                                                               'folder of your documenation')
        parser.add_argument('-y', action='store_true', help='overwrite the output without asking')

        parser.add_argument('-D',"--dry", action='store_true', help='Dry runt without writing')

        parser.add_argument("--sample-config", action='store_true', help='Print the sample configuration yaml file')

        parser.add_argument('-p', nargs='?', default="_unset_", help='use print template instead of writing to files, '
                                                                     'sections: all, info, tags, todo, var')

        parser.add_argument('-V',"--version", action='store_true', help='Get versions')

        debug_level = parser.add_mutually_exclusive_group()
        debug_level.add_argument('-v', action='store_true', help='Set debug level to info')
        debug_level.add_argument('-vv', action='store_true', help='Set debug level to debug')
        debug_level.add_argument('-vvv', action='store_true', help='Set debug level to trace')

        return parser.parse_args()

    def _parse_args(self,args):
        """
        Use an args object to apply all the configuration combinations to the config object
        :param args:
        :return: None
        """
        self.config.set_base_dir(os.path.abspath(args.project_dir))

        # search for config file
        if args.conf != "":
            conf_file = os.path.abspath(args.conf)
            if os.path.isfile(conf_file) and os.path.basename(conf_file) == self.config.config_file_name:
                self.config.load_config_file(conf_file)
                # re apply log level based on config
                self.log.set_level(self.config.debug_level)
            else:
                self.log.warn("No configuration file found: "+conf_file)
        else:
            conf_file = self.config.get_base_dir()+"/"+self.config.config_file_name
            if os.path.isfile(conf_file):
                self.config.load_config_file(conf_file)
                # re apply log level based on config
                self.log.set_level(self.config.debug_level)

        # sample configuration
        if args.sample_config:
            print(self.config.sample_config)
            sys.exit()

        # version
        if args.version:
            print(__version__)
            sys.exit()

        # Debug levels
        if args.v is True:
            self.log.set_level("info")
        elif args.vv is True:
            self.log.set_level("debug")
        elif args.vvv is True:
            self.log.set_level("trace")

        # need to send the message after the log levels have been set
        self.log.debug("using configuration file: "+conf_file)

        # Overwrite
        if args.y is True:
            self.config.template_overwrite = True

        # Dry run
        if args.dry is True:
            self.config.dry_run = True
            if self.log.log_level > 1:
                self.log.set_level(1)
                self.log.info("Running in Dry mode: Therefore setting log level at least to INFO")

        # Print template
        if args.p == "_unset_":
            pass
        elif args.p is None:
            self.config.use_print_template = "all"
        else:
            self.config.use_print_template = args.p

        # output dir
        if args.output is not None:
            self.config.output_dir = os.path.abspath(args.output)

        # some debug
        self.log.debug(args)
        self.log.info("Using base dir: "+self.config.get_base_dir())

        if self.config.is_role:
            self.log.info("This is detected as: ROLE ")
        elif self.config.is_role is not None and not self.config.is_role:
            self.log.info("This is detected as: PLAYBOOK ")
        else:
            self.log.error([
                self.config.get_base_dir()+"/roles",
                self.config.get_base_dir()+"/tasks"
            ],"No ansible root project found, checked for: ")
            sys.exit(1)
