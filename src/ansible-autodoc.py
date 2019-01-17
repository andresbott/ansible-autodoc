#!/usr/bin/env python3

import os
import sys
import argparse
import glob
import yaml
import re

from utils import log,utils


class AnsibleAutodoc:


    debug_level = "debug"
    plugin_annotations = "annotations.yaml"

    output_dir = ""
    base_dir = ""
    plugin_install_dir = ""
    annotations_definitions = None
    yaml_files_playbook = []
    yaml_files_roles = {}
    is_role = None

    # todo: move to future config
    excluded_playbook_dirs = [
        "host_vars",
        "group_vars",
        "host_secrets",
        "plugins",
        "autodoc.config.yaml"
    ]

    excluded_roles_dirs = [
        "handlers",
    ]

    def __init__(self):
        self.log = log.SingleLog(self.debug_level)

        self.plugin_install_dir = os.path.dirname(os.path.abspath(__file__))
        self._load_config()
        self._args()

        self._find_yaml_files()

        self.log.debug(self.yaml_files_playbook,"PLAYBOOK")
        self.log.debug(self.yaml_files_roles,"ROLES")
        self.log.debug(self.annotations_definitions,"Annotations")

    def _args(self):
        usage = '''TODO: add usage

        '''
        parser = argparse.ArgumentParser(description='Generate Ansible Documentation', usage=usage)
        # parser.add_argument("-f", "--force", help="Force online list", action="store_true")
        # parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag', required=True)
        parser.add_argument('-t','--type', nargs='+', help='<Required> Set flag')
        parser.add_argument('dir', nargs='?', default=os.getcwd())
        parser.add_argument('-o', action="store", dest="out", type=str)

        args = parser.parse_args()

        self.base_dir = os.path.abspath(args.dir)
        if args.out is None:
            self.output_dir = os.path.abspath(os.getcwd()+"/doc")
        else:
            self.output_dir = os.path.abspath(args.out)

        if os.path.isdir(self.base_dir+"/roles" ):
            self.is_role = False
        elif os.path.isdir(self.base_dir+"/tasks" ):
            self.is_role = True
            self.role_name = os.path.basename(self.base_dir)
        else:
            print("Error: I cloud not find a project nor a role to document: \n"
                  " I checked for: "+ self.base_dir+"/roles (project) \n"
                                                    " and:  "+ self.base_dir+"/tasks (role)" )
            sys.exit(1)

        # print(args)
        # print("base dir: "+self.base_dir)
        # print("out dir: "+self.output_dir)
        # print("is Role: "+str(self.is_role))

    def _load_config(self):
        """
        Load configurations into the execution environment
        :return: None
        """
        file = self.plugin_install_dir+"/"+self.plugin_annotations
        self.annotations_definitions = utils.Utils.load_yaml(file)


    def _find_yaml_files(self):
        """
        Search for Yaml files depending if we are scanning a playbook or a role
        :return:
        """
        if not self.is_role:
            self.log.debug("Scan for playbook files")
            self._scan_for_yamls(self.base_dir,is_role=False)

            self.log.debug("Scan for roles in the project")
            base_dir = self.base_dir+"/roles"

            for entry in os.scandir(base_dir):
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError as error:
                    print('Error calling is_dir():', error, file=sys.stderr)
                    continue
                if is_dir:
                    self._scan_for_yamls(entry.path)
        else:  # it is a role
            self.log.debug("Scan for files in a role")
            base_dir= self.base_dir
            self._scan_for_yamls(base_dir)

    def _scan_for_yamls(self,base,is_role=True):
        """
        Search fror the yaml files
        :param base: directory in witch we are searching
        :param is_role: is this a role directory
        :return: None
        """
        extensions = ["yaml","yml"]
        base_dir = base

        for extension in extensions:
            for filename in glob.iglob(base_dir+'/**/*.'+extension, recursive=True):

                if self._is_excluded_yaml_file(filename,base_dir,is_role=is_role):
                    self.log.trace("Excluding: "+filename)

                else:
                    if not is_role:
                        self.log.trace("Adding to playbook: "+filename)
                        self.yaml_files_playbook.append(filename)
                    else:
                        role_dir = os.path.basename(base_dir)
                        self.log.trace("Adding to role:"+role_dir+" => "+filename)
                        if role_dir not in self.yaml_files_roles:
                            self.yaml_files_roles[role_dir] = []

                        self.yaml_files_roles[role_dir].append(filename)


    def _is_excluded_yaml_file(self, file,role_base_dir=None,is_role=True):
        """
        sub method for handling file exclusions based on the full path starts with
        :param file:
        :param role_base_dir:
        :param is_role:
        :return:
        """

        if is_role:
            base_dir = role_base_dir
            excluded = self.excluded_roles_dirs
        else:
            base_dir = self.base_dir
            excluded = self.excluded_playbook_dirs
            excluded.append("roles")

        is_filtered = False
        for excluded_dir in excluded:
            if file.startswith(base_dir+"/"+excluded_dir):
                return True
        return is_filtered





    def find_tags_in_yaml(self):
        pass

    def find_annotations_in_yaml(self):
        pass


if __name__ == "__main__":
    doc = AnsibleAutodoc()
    # doc.find_yamls()
    #
    #
    #
    # doc.print_doc()
    # print()
    # doc.print_report()

