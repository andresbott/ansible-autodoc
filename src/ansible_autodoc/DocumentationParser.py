#!/usr/bin/env python3

import yaml
import re

from ansible_autodoc.Utils import SingleLog
from ansible_autodoc.Config import SingleConfig
from ansible_autodoc.FileRegistry import Registry


class Parser:

    log = None
    config = None
    files_registry = None
    doc_data = None

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
                tmp_r = Parser.find_tag(key, d)
                if tmp_r:
                    r = Parser.merge_list_no_duplicates(r,tmp_r)

        elif isinstance(data,dict):
            for k,d in data.items():
                if k == key:
                    r = r + d
                else:
                    tmp_r = Parser.find_tag(key, d)
                    if tmp_r:
                        r = Parser.merge_list_no_duplicates(r,tmp_r)
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
        self.config = SingleConfig()
        self.log = SingleLog()
        self.files_registry = Registry()
        self.generate_doc_data()

    def get_data(self):
        return self.doc_data

    def generate_doc_data(self):
        """
        Generate the documentation data object
        """
        r = {}
        self.log.debug("Generate Doc data")

        tags = self._find_tags_in_yaml()
        tag_annotations = self._fin_annotation(self.config.annotations["tag"]["regex"])
        parsed_tags = self._parse_tag(tags,tag_annotations)
        self.log.trace(parsed_tags,"Parsed Tags")

        r["tags"] = parsed_tags

        self.doc_data = r

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
                elif not self.config.is_role and yaml_tag_key in tag_annotations["_roles_"]["_ansible_playbook_"].keys():
                    r["_roles_"][role][yaml_tag_key] = tag_annotations["_roles_"]["_ansible_playbook_"][yaml_tag_key]
                else:
                    r["_roles_"][role][yaml_tag_key] = yaml_tag_value

        # yaml duplicates
        r["_yaml_duplicate_"] = yaml_tags["_duplicate_"]

        # annotation duplicates
        r["_annotation_duplicate_"] = tag_annotations["_duplicate_"]

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
                        tags_found = Parser.find_tag("tags",data)

                        for found_tag in tags_found:
                            if found_tag not in self.config.excluded_tags:

                                tag = Parser._gen_tag_doc(found_tag,role=file_group_key)

                                # all tags
                                if found_tag not in tags["_all_"].keys():
                                    tags["_all_"][found_tag] = tag

                                # if already in all tags, check if its from the same role
                                # if not, add to duplicate
                                elif file_group_key != tags["_all_"][found_tag]["role"]:
                                    if found_tag not in tags["_duplicate_"]:
                                        tags["_duplicate_"][found_tag] = []
                                        tags["_duplicate_"][found_tag].append(tags["_all_"][found_tag])
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

                        item = Parser._gen_tag_doc(doc_key, text=doc_data, role=role, file=file,
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

