#!/usr/bin/env python3

import os

from ansibleautodoc.Utils import SingleLog
from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.FileRegistry import Registry
from ansibleautodoc.Annotation import Annotation
from ansibleautodoc.Contstants import *


class MocParser:

    config = None

    def __init__(self):
        self.config = SingleConfig

    def get_data(self):
        return {}

class Parser:

    log = None
    config = None
    _files_registry = None
    _annotation_data = {}
    _annotation_objs = {}

    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog()
        self._files_registry = Registry()
        self._populate_doc_data()

    def _populate_doc_data(self):
        """
        Generate the documentation data object
        """
        for annotaion in self.config.get_annotations_names(special=True, automatic=True):
            self.log.info("Finding annotations for: @"+annotaion)
            self._annotation_objs[annotaion] = Annotation(name=annotaion, files_registry=self._files_registry)
            self._annotation_data[annotaion] = self._annotation_objs[annotaion].get_details()

    def get_data(self):
        return self._annotation_data

    def get_annotations(self):
        return self._annotation_data.keys()

    def get_roles(self,exclude_playbook=True):
        roles = list (self._files_registry.get_files().keys())
        if PLAYBOOK_ROLE_NAME in roles and exclude_playbook:
            roles.remove(PLAYBOOK_ROLE_NAME)
        return roles

    def include(self,filename):
        base =self.config.get_base_dir()
        base += "/"+filename
        base = os.path.abspath(base)
        self.log.debug("try to include:"+base)
        if os.path.isfile(base):
            text_file = open(base, "r")
            lines = text_file.readlines()
            out = ""
            for line in lines:
                out += line
            return out
        else:
            # return "[include] file: "+base+" not found"
            return ""

    def is_role(self):
        return self.config.is_role

    def get_name(self):
        return self.config.project_name

    def cli_print_section(self):
        return self.config.use_print_template

    def _get_annotation(self,name,role="all",return_keys=False,return_item=None,return_multi=False):
        if name in self._annotation_objs.keys():
            data = self._annotation_objs[name].get_details()

            if role == "all":
                r_data = data["all"]
            elif role in data["role_items"].keys():
                r_data = data["role_items"][role]
            elif role == "play" and PLAYBOOK_ROLE_NAME in data["role_items"].keys():
                r_data = data["role_items"][PLAYBOOK_ROLE_NAME]
            else:
                r_data = {}

            if return_keys:
                print(list(r_data.keys()))
                return list(r_data.keys())
            elif isinstance(return_item,str):
                if return_item in r_data.keys():
                    return r_data[return_item]
                else:
                    return ""
            elif return_multi and self.allow_multiple(name):
                return r_data.items()
            else:
                if self.allow_multiple(name):
                    # return r_data
                    r = []
                    for k,v in r_data.items():
                        for item in v:
                            r.append(item)
                    return r
                else:
                    r = []
                    for k,v in r_data.items():
                        r.append(v)
                    return r

        else:
            return None

    def get_type(self,name,role="all"):
        return self._get_annotation(name,role)

    def get_multi_type(self,name,role="all"):
        return self._get_annotation(name,role,return_multi=True)

    def get_keys(self,name,role="all"):
        return self._get_annotation(name,role,True)

    def get_item(self,name,key,role="all"):
        return self._get_annotation(name,role,False,key)

    def get_duplicates(self,name):
        if name in self._annotation_objs.keys():
            data = self._annotation_objs[name].get_details()
            return data["duplicates"].items()

    def has_items(self,name,role="all"):
        if len(self._get_annotation(name,role)) > 0:
            return True
        else:
            return False

    def allow_multiple(self,name):
        if name in self.config.annotations:
            if "allow_multiple" in self.config.annotations[name].keys() and self.config.annotations[name]["allow_multiple"]:
                return True
        return False

    def cli_left_space(self,item1="",l=25):
        item1 = item1.ljust(l)
        return item1

    def capitalize(self,s):
        return s.capitalize()

    def fprn(self,string,re="Playbook"):
        if string == "_ansible_playbook_":
            return re
        else:
            return string
    def about(self,l="md"):
        if l == "md":
            return "Documentation generated using: ["+self.config.autodoc_name+"]("+self.config.autodoc_url+")"

    def test(self):
        return "test()"

















