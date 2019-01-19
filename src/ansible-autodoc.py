#!/usr/bin/env python3

import os
import sys
import argparse
import glob
import yaml
import re

from utils import log,utils
from utils.singleton import Singleton


class AnsibleAutodocConfig:

    output_dir = ""
    base_dir = ""
    debug_level = "info"
    is_role = None
    role_name = ""

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

    annotations = {
        "tag":{
            "name":"tag",
            "regex":"(\#\ *\@tag:\ *.*\:\ *.*)"
        }
    }

    # special Ansible tags to be removed from the tag list
    excluded_tags= [
        "always",
        "untagged",
        "never",
        "untagged",
    ]

    def __init__(self):
        pass


class SingAnsibleAutodocConfig(AnsibleAutodocConfig,metaclass=Singleton):
    pass


class AnsibleAutodocRegistry:

    _doc = {
        "_ansible_playbook_" : []
    }
    log = None
    config = None


    def __init__(self):
        self.config = SingAnsibleAutodocConfig()
        self.log = log.SingleLog()

        self._find_yaml_files()

    def get_file(self,name):
        if name in self._doc.keys():
            return self._doc[name]
        else:
            return None

    def get_files(self,role=None):
        r = []
        if not role:
            return self._doc
        else:
            for k,v in self._doc.items():
                print(k)
                print(v)


    def _find_yaml_files(self):
        """
        Search for Yaml files depending if we are scanning a playbook or a role
        :return:
        """
        base_dir = self.config.base_dir
        base_dir_roles = base_dir+"/roles"

        if not self.config.is_role:
            self.log.debug("Scan for playbook files: "+base_dir)
            self._scan_for_yamls(base_dir,is_role=False)

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
                        self.add_playbook_file(filename)
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
            excluded = self.config.excluded_roles_dirs
        else:
            base_dir = self.config.base_dir
            excluded = self.config.excluded_playbook_dirs
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

    def add_playbook_file(self,path):
        self.log.trace("add_playbook_file("+path+")")
        self._doc["_ansible_playbook_"].append(path)



class AnsibleAutodoc:

    log = None
    config = None
    files_registry = None

    @staticmethod
    def _gen_tag_doc(tag,text="",role="",file="",line=""):
        return {
            "tag":tag,
            "text":text,
            "role":role,
            "file":file,
            "line":line
        }

    @staticmethod
    def find_tag(key,data):

        r = []
        if isinstance(data,list):
            for d in data:
                tmp_r = AnsibleAutodoc.find_tag(key, d)
                if tmp_r:
                    r = AnsibleAutodoc.merge_list_no_duplicates(r,tmp_r)

        elif isinstance(data,dict):
            for k,d in data.items():
                if k == key:
                    r = r + d
                else:
                    tmp_r = AnsibleAutodoc.find_tag(key, d)
                    if tmp_r:
                        r = AnsibleAutodoc.merge_list_no_duplicates(r,tmp_r)
        return r

    @staticmethod
    def merge_list_no_duplicates(a1,a2):
        """
        merge two lists by overwriting the original with the second one if the key exists
        :param a1:
        :param a2:
        :return:
        """
        r = []
        if isinstance(a1,list) and isinstance(a2,list):
            r = a1
            for i in a2:
                if i not in a1:
                    r.append(i)
        return r

    def __init__(self):
        self.config = SingAnsibleAutodocConfig()
        self.log = log.SingleLog(self.config.debug_level)

        self._args()

        self.files_registry = AnsibleAutodocRegistry()

        self.generate_doc_data()

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

    def generate_doc_data(self):
        """
        Generate the documentation data object
        :return:
        """
        self.log.debug("Generate Doc data")
        tags = self._find_tags_in_yaml()
        tag_annotations = self._fin_annotation(self.config.annotations["tag"]["regex"])

        parsed_tags = self._parse_tag(tags,tag_annotations)

    def _parse_tag(self,yaml_tags,tag_annotations):
        """
        Merge yaml found tags, with annotation found tags
        :param yaml_tags:
        :param annotations_tags:
        :return:
        """
        self.log.trace(yaml_tags,"yaml_tags")
        self.log.trace(tag_annotations,"annotations_tags")
        r = {
            "_all_":{},
            "_roles_":{},
            "_yaml_duplicate_":{},
            "_annotation_duplicate_":{}
        }
        if "_report_" in tag_annotations.keys():
            tag_annotations.pop("_report_")

        # _all_
        for yaml_tag_key, yaml_tag_value in yaml_tags["_all_"].items():
            if yaml_tag_key in tag_annotations["_all_"].keys():
                r["_all_"][yaml_tag_key] = tag_annotations["_all_"][yaml_tag_key]
            else:
                r["_all_"][yaml_tag_key] = yaml_tag_value

        # _roles_
        for role,role_data in yaml_tags["_roles_"].items():
            for yaml_tag_key, yaml_tag_value in role_data.items():

                if role not in r["_roles_"].keys():
                    r["_roles_"][role] = {}

                if yaml_tag_key in tag_annotations["_roles_"][role].keys():
                    r["_roles_"][role][yaml_tag_key] = tag_annotations["_roles_"][role][yaml_tag_key]
                # if defined in the playbook => overwrite
                elif yaml_tag_key in tag_annotations["_roles_"]["_ansible_playbook_"].keys():
                    r["_roles_"][role][yaml_tag_key] = tag_annotations["_roles_"]["_ansible_playbook_"][yaml_tag_key]
                else:
                    r["_roles_"][role][yaml_tag_key] = yaml_tag_value

        # yaml duplicates
        r["_yaml_duplicate_"] = yaml_tags["_duplicate_"]

        # annotation duplicates
        r["_annotation_duplicate_"] = tag_annotations["_duplicate_"]
        self.log.trace(r)

        return r

    def _find_tags_in_yaml(self):
        """
        Load and parse a yaml file and search for the tags element
        used to identify tags used in the playbook and roles
        :param self:
        :return:
        """

        tags = {
            "_all_" : {},
            "_duplicate_" : {},
            "_roles_": {}
        }

        for file_group_key, file_group_list in self.files_registry.get_files().items():
            for file in file_group_list:
                with open(file, 'r') as yaml_file:
                    try:
                        data = yaml.load(yaml_file)
                        tags_found = AnsibleAutodoc.find_tag("tags",data)

                        for found_tag in tags_found:
                            if found_tag not in self.config.excluded_tags:

                                tag = AnsibleAutodoc._gen_tag_doc(found_tag,role=file_group_key)

                                # all tags
                                if found_tag not in tags["_all_"].keys():
                                    tags["_all_"][found_tag] = tag

                                # if already in all tags, check if its from the same role
                                # if not, add to duplicate
                                elif file_group_key != tags["_all_"][found_tag]["role"]:
                                    if found_tag not in tags["_duplicate_"]:
                                        tags["_duplicate_"][found_tag] = []
                                    tags["_duplicate_"][found_tag].append(tag)

                                # per role
                                if file_group_key not in tags["_roles_"].keys():
                                    tags["_roles_"][file_group_key] = {}
                                if found_tag not in tags["_roles_"][file_group_key].keys():
                                    tags["_roles_"][file_group_key][found_tag] = tag

                    except yaml.YAMLError as exc:
                        print(exc)

        return tags

    def _fin_annotation(self,regex=""):
        """
        Make use of the passed regex to generate a json structure with the results of the scan
        :param regex:
        :return:
        """
        r = {
            "_all_" : {},
            "_duplicate_" : {},
            "_roles_": {},
        }
        if regex == "":
            return r

        for role, files_in_role in self.files_registry.get_files().items():

            for file in files_in_role:
                fh = open(file)
                line_number = 1
                while True:
                    line = fh.readline()
                    match = re.match(regex, line)

                    if match:

                        base_line = line.strip()[1:].strip().split(":")
                        if len(base_line) > 2:
                            # example: @tag: enroll : for quick initial enrolment of the system
                            doc_key = base_line[1].strip()
                            doc_data = base_line[2].strip()

                        else:
                            # example: @author: Andres Bott
                            doc_key = base_line[0].strip()
                            doc_data = base_line[1].strip()

                        item = AnsibleAutodoc._gen_tag_doc(doc_key, text=doc_data, role=role, file=file,
                                                           line=line_number)

                        # all files
                        if doc_key not in r["_all_"].keys():
                            r["_all_"][doc_key] = item

                        else:
                            # duplicated
                            if doc_key not in r["_duplicate_"]:
                                r["_duplicate_"][doc_key] = []
                                r["_duplicate_"][doc_key].append(r["_all_"][doc_key])
                            r["_duplicate_"][doc_key].append(item)


                        # # if already in _all_, check if its from the same role
                        # # if not, add to duplicate
                        # elif role != r["_all_"][doc_key]["role"]:
                        #     if doc_key not in r["_duplicate_"]:
                        #         r["_duplicate_"][doc_key] = []
                        #     r["_duplicate_"][doc_key].append(item)

                        # per role
                        if role not in r["_roles_"].keys():
                            r["_roles_"][role] = {}
                        if doc_key not in r["_roles_"][role].keys():
                            r["_roles_"][role][doc_key] = item

                    line_number += 1
                    if not line:
                        break
                fh.close()
        return r




if __name__ == "__main__":
    doc = AnsibleAutodoc()
    # doc.find_yamls()
    #
    #
    #
    # doc.print_doc()
    # print()
    # doc.print_report()

