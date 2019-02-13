#!/usr/bin/env python3

import yaml
import re
import pprint

from ansibleautodoc.Utils import SingleLog
from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.FileRegistry import Registry


class Parser:

    log = None
    config = None
    files_registry = None
    doc_data = None

    @staticmethod
    def _anottation(key,value="",text="",role="",file="",line=""):
        return {
            "key":key,
            "value":value,
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
                    if isinstance(d,str):
                        d = [d]
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
        r = {
            "is_role": self.config.is_role,
            "is_print": self.config.use_print_template
        }

        # take care of special use case tags
        self.log.info("Searching for tags in use in the project...")
        tags = self._find_tags_in_yaml()
        self.log.info("Finding annotations for: @tag")
        tag_annotations = self._fin_annotation(self.config.annotations["tag"])
        parsed_tags = self._parse_tag(tags,tag_annotations)
        self.log.trace(parsed_tags,"Parsed Tags")
        r["tags"] = parsed_tags

        # simple annotations that follow all the same pattern, like author and description
        automatic_annotations = []
        for k, automatic_annotation in self.config.annotations.items():
            if "automatic" in automatic_annotation.keys() and automatic_annotation:
                automatic_annotations.append(automatic_annotation["name"])

        for simple_annotation in automatic_annotations:
            self.log.info("Finding annotations for: @"+simple_annotation)
            data = self._fin_annotation(self.config.annotations[simple_annotation])
            self.log.trace(data, "Results for: @"+simple_annotation)
            r[simple_annotation] = data

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
                if role in tag_annotations["_roles_"].keys() and yaml_tag_key in tag_annotations["_roles_"][role].keys():
                    r["_roles_"][role][yaml_tag_key] = tag_annotations["_roles_"][role][yaml_tag_key]
                # if defined in the playbook => overwrite
                elif not self.config.is_role and "_ansible_playbook_" in tag_annotations["_roles_"].keys() \
                        and yaml_tag_key in tag_annotations["_roles_"]["_ansible_playbook_"].keys():
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
                with open(file, 'r',encoding='utf8') as yaml_file:
                    try:
                        data = yaml.load(yaml_file)
                        tags_found = Parser.find_tag("tags",data)

                        for found_tag in tags_found:
                            if found_tag not in self.config.excluded_tags:

                                tag = Parser._anottation(found_tag,role=file_group_key)

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

    def _fin_annotation(self, rules):
        """
        Make use of the passed regex to generate a json structure with the results of the scan
        :param regex:
        :return:
        """
        r = {
            "_all_" : {},
            "_duplicate_" : {},
            "_roles_": { },
            "_keys_": [],
        }
        regex = "(\#\ *\@"+rules["name"]+"\ *\: *.*)"

        for role, files_in_role in self.files_registry.get_files().items():

            last_annotation_item = None
            is_block_content = None

            for file in files_in_role:
                fh = open(file,encoding='utf8')
                line_number = 1
                while True:
                    line = fh.readline()

                    if re.match(self.config.annotations["example"]["regex"], line):
                        # match for a block object like @example
                        # if we match, then we use the previous defined item
                        if last_annotation_item:
                            a_item = self._get_annotation_data(line, self.config.annotations["example"])
                            a_item["role"] = role
                            a_item["file"] = file
                            a_item["line"] = line_number
                            a_item["multi_line"] = []
                            is_block_content = a_item

                    elif (re.match(self.config.annotations["block_end"]["regex"], line) or line.strip()[:1] != "#" ) \
                            and is_block_content:
                        # match for a end of block object like @example
                        # assign the collected lines to last annotation content
                        last_annotation_item["example"] = is_block_content
                        is_block_content = None
                        last_annotation_item = None

                    elif is_block_content and line.strip()[:1] == "#":
                        # add the lines that start with a comment, minus the comment
                        is_block_content["multi_line"].append(line.strip()[1:])

                    elif re.match(regex, line):
                        # regular lines matching
                        item = self._get_annotation_data(line, rules)
                        item["role"] = role
                        item["file"] = file
                        item["line"] = line_number

                        last_annotation_item = item

                        self._assign_to_r(r,item,role,rules)

                    line_number += 1
                    if not line:
                        break
                fh.close()
        return r

    def _assign_to_r(self,r,item,role,rules):
        key = item["key"]

        if key not in r["_keys_"]:
            r["_keys_"].append(key)

        if "allow_multiple" in rules.keys() and rules["allow_multiple"]:
            # all files
            if "_items_" not in r["_all_"].keys():
                r["_all_"]["_items_"]=[]
            r["_all_"]["_items_"].append(item)

            # per role
            if role not in r["_roles_"].keys():
                r["_roles_"][role] = []
            r["_roles_"][role].append(item)

        else:

            # all files
            if key not in r["_all_"].keys():
                r["_all_"][key] = item

            else:
                # duplicated
                if key not in r["_duplicate_"]:
                    r["_duplicate_"][key] = []
                    r["_duplicate_"][key].append(r["_all_"][key])
                r["_duplicate_"][key].append(item)

            # per role
            if role not in r["_roles_"].keys():
                r["_roles_"][role] = {}
            if key not in r["_roles_"][role].keys():
                r["_roles_"][role][key] = item

    def _get_annotation_data(self,line,rules=None):
        """
        make some string conversion on a line in order to get the relevant data
        :param line:
        :return: [key,value]
        """
        r = []
        if not rules:
            return r
        annotation_name= rules["name"]

        # step1 remove the annotation
        reg1 =  "(\#\ *\@"+annotation_name+"\ *\: *)"
        line1 = re.sub(reg1, '', line)

        # step2 split annotation and comment by #
        parts = line1.split("#")

        value = ""
        if len(parts)>1:
            key = parts[0].strip()

            sub_parts = key.split(":")

            if len(sub_parts) > 1:
                key = sub_parts[0].strip()
                value = sub_parts[1].strip()

            text = parts[1].strip()

        else:
            key = annotation_name
            text = parts[0].strip()

        if len(key) == 0:
            key= "_undef_"
        item = Parser._anottation(
            key,
            value = value.strip(),
            text = text.strip()
        )

        return item




