#!/usr/bin/env python3
import os
import sys
import glob

from ansibleautodoc.Contstants import *
from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.Utils import SingleLog


class Registry:

    _doc = {}
    log = None
    config = None

    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog()
        self._scan_for_yamls_in_project()

    def get_files(self):
        """
        :return objcect structured as:
            {
                "role_name":["/abs_path/to_file","/abs_path/to_file2"],
                "role2_name:["abs/path/2"]
            }
        :param
        :return:
        """
        return self._doc

    def _scan_for_yamls_in_project(self):
        """
        Search for Yaml files depending if we are scanning a playbook or a role
        :return:
        """
        base_dir = self.config.get_base_dir()
        base_dir_roles = base_dir+"/roles"

        if not self.config.is_role:

            self.log.debug("Scan for playbook files: "+base_dir)
            self._scan_for_yamls(base_dir, is_role=False)

            self.log.debug("Scan for roles in the project: "+base_dir_roles)
            for entry in os.scandir(base_dir_roles):
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                except OSError as error:
                    print('Error calling is_dir():', error, file=sys.stderr)
                    continue
                if is_dir:
                    self._scan_for_yamls(entry.path)
        else:  # it is a role
            self.log.debug("Scan for files in a role: "+base_dir)
            self._scan_for_yamls(base_dir)

    def _scan_for_yamls(self,base,is_role=True):
        """
        Search for the yaml files in each project/role root and append to the corresponding object
        :param base: directory in witch we are searching
        :param is_role: is this a role directory
        :return: None
        """
        extensions = YAML_EXTENSIONS
        base_dir = base

        for extension in extensions:
            for filename in glob.iglob(base_dir+'/**/*.'+extension, recursive=True):

                if self._is_excluded_yaml_file(filename,base_dir,is_role=is_role):
                    self.log.trace("Excluding: "+filename)

                else:
                    if not is_role:
                        self.log.trace("Adding to playbook: "+filename)
                        self.add_role_file(filename, PLAYBOOK_ROLE_NAME)
                    else:
                        role_dir = os.path.basename(base_dir)
                        self.log.trace("Adding to role:"+role_dir+" => "+filename)
                        self.add_role_file(filename,role_dir)

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
            excluded = self.config.excluded_roles_dirs.copy()
        else:
            base_dir = self.config.get_base_dir()
            excluded = self.config.excluded_playbook_dirs.copy()
            excluded.append("roles")

        is_filtered = False
        for excluded_dir in excluded:
            if file.startswith(base_dir+"/"+excluded_dir):
                return True
        return is_filtered

    def add_role_file(self,path,role_name):
        self.log.trace("add_role_file("+path+","+role_name+")")
        if role_name not in self._doc.keys():
            self._doc[role_name] = []

        self._doc[role_name].append(path)

