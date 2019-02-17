#!/usr/bin/env python3

import yaml
import re
import pprint

from ansibleautodoc.Utils import SingleLog
from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.FileRegistry import Registry


class AnnotationItem:

    key = ""  # annotation identifying key
    value = ""  # annotation data
    desc = ""  # annotation longer description
    role = ""  # associated role
    file = ""  # file of the annotation
    line = ""  # line of the annotation
    example = ""  # add an example item iof defined: @example

    # next time improve this by looping over public available attributes
    def __str__(self):
        s = "{"
        s += "key: "+self.key+", "
        s += "value: "+self.value+", "
        s += "desc: "+self.desc+", "
        s += "role: "+self.role+", "
        s += "file: "+self.file+", "
        s += "line: "+self.line+" "
        s += "line: "+self.example+" "
        s += "}"
        return s

    def get_obj(self):
        return {
            "key": self.key,
            "value": self.value,
            "desc": self.desc,
            "role": self.role,
            "file": self.file,
            "line": self.line,
            "example": self.example,
        }


class Annotation:

    _files_registry = None  # reference to current file registry
    _annotation_definition = None  # current annotation definition
    _all_annotations = None  # reference to defined annotation definition
    _allow_multiple = None

    _current_file = None
    _current_file_pos = None
    _current_role = None
    _current_line = None
    _file_handler = None

    _all_items = {}
    _duplucate_items = {}
    _role_items = {}

    def __init__(self,name,files_registry):
        self.config = SingleConfig()
        self.log = SingleLog()
        self._files_registry = files_registry

        self._all_annotations = self.config.get_annotations_definition()

        if name in self._all_annotations.keys():
            self._annotation_definition = self._all_annotations[name]

            # check for allow multiple
            if "allow_multiple" in self._annotation_definition.keys() and self._annotation_definition["allow_multiple"] == True:
                self._allow_multiple = True

            else:
                self._allow_multiple = False

            self._role_items = {}
            self._all_items = {}
            self._duplucate_items = {}

        if self._annotation_definition is not None:
            self._find_annotation()

        if "special" in self._annotation_definition.keys() and self._annotation_definition["special"]:
            if name == "tag":
                self._find_tags()


    def get_details(self):
        return {
            "all": self._all_items,
            "duplicates": self._duplucate_items,
            "role_items": self._role_items,
        }

    def _find_annotation(self):

        regex = "(\#\ *\@"+self._annotation_definition["name"]+"\ +.*)"
        for role, files_in_role in self._files_registry.get_files().items():

            for file in files_in_role:
                # reset stats
                self._current_line = 1
                self._current_file = file
                self._current_role = role
                self._file_handler = open(file, encoding='utf8')
                self._current_file_pos = 0

                while True:
                    line = self._file_handler.readline()
                    if not line:
                        break

                    if re.match(regex, line):
                        item = self._get_annotation_data(line,self._annotation_definition["name"])
                        # print(item.get_obj())
                        self._populate_item(item)

                    self._current_line += 1
                self._file_handler.close()

    def _populate_item(self,item):

        if self._allow_multiple:
            # all items
            if item.key not in self._all_items.keys():
                self._all_items[item.key] = []

            self._all_items[item.key].append(item.get_obj())

            if item.role not in self._role_items.keys():
                self._role_items[item.role] = {}

            if item.key not in self._role_items[item.role].keys():
                self._role_items[item.role][item.key] = []

            self._role_items[item.role][item.key].append(item.get_obj())

        else:

            if item.key not in self._all_items.keys():
                self._all_items[item.key] = item.get_obj()
            else:
                # add to duplicates
                print("Dup:" + str(item.key))
                if item.key not in self._duplucate_items.keys():
                    self._duplucate_items[item.key] = []
                    self._duplucate_items[item.key].append(self._all_items[item.key])
                self._duplucate_items[item.key].append(item.get_obj())

            # role items
            if item.role not in self._role_items.keys():
                self._role_items[item.role] = {}

            if item.key not in self._role_items[item.role].keys():
                self._role_items[item.role][item.key] = item.get_obj()

    def _get_annotation_data(self,line,name):
        """
        make some string conversion on a line in order to get the relevant data
        :param line:
        """
        item = AnnotationItem()

        # fill some more data
        if self._current_file:
            item.file = self._current_file
        if self._current_role:
            item.role = self._current_role
        if self._current_line:
            item.line = self._current_line

        # step1 remove the annotation
        # reg1 = "(\#\ *\@"++"\ *)"
        reg1 = "(\#\ *\@"+name+"\ *)"
        line1 = re.sub(reg1, '', line).strip()

        # print("line1: '"+line1+"'")
        # step2 split annotation and comment by #
        parts = line1.split("#")

        # step3 take the main key value from the annotation
        subparts = parts[0].split(":")

        key = str(subparts[0].strip())
        if key.strip() == "":
            key = "_unset_"
        item.key = key

        if len(subparts)>1:
            item.value = subparts[1].strip()

        # step4 check for multiline description
        multiline = ""
        stars_with_annotation = '(\#\ *[\@][\w]+)'
        current_file_position = self._file_handler.tell()

        while True:
            next_line = self._file_handler.readline()

            if not next_line.strip():
                self._file_handler.seek(current_file_position)
                break

            # match if annotation in line
            if re.match(stars_with_annotation, next_line):
                self._file_handler.seek(current_file_position)
                break
            # match if empty line or commented empty line
            test_line = next_line.replace("#", "").strip()
            if len(test_line) == 0:
                self._file_handler.seek(current_file_position)
                break

            # match if does not start with comment
            test_line2 = next_line.strip()
            if test_line2[:1] != "#":
                self._file_handler.seek(current_file_position)
                break

            if name == "example":
                multiline += next_line.replace("#", "", 1)
            else:
                multiline += " "+test_line.strip()

        # step5 take the description, there is something after #
        if len(parts) > 1:
            desc = parts[1].strip()
            desc += " "+multiline.strip()
            item.desc = desc.strip()
        elif multiline != "":
            item.desc = multiline.strip()

        # step5, check for @example
        example = ""

        if name != "example":

            current_file_position = self._file_handler.tell()
            example_regex = "(\#\ *\@example\ +.*)"

            while True:
                next_line = self._file_handler.readline()
                if not next_line:
                    self._file_handler.seek(current_file_position)
                    break

                # exit if next annotation is not @example
                if re.match(stars_with_annotation, next_line):
                    if "@example" not in next_line:
                        self._file_handler.seek(current_file_position)
                        break

                if re.match(example_regex, next_line):
                    example = self._get_annotation_data(next_line,"example")
                    # pprint.pprint(example.get_obj())
                    self._file_handler.seek(current_file_position)
                    break
        if example != "":
            item.example = example.get_obj()

        return item

    def _find_tags(self):
        for role, files_in_role in self._files_registry.get_files().items():
            for file in files_in_role:

                with open(file, 'r',encoding='utf8') as yaml_file:
                    try:
                        data = yaml.load(yaml_file)
                        tags_found = Annotation.find_tag("tags",data)

                        for tag in tags_found:
                            if tag not in self.config.excluded_tags:

                                item = AnnotationItem()
                                item.file = file
                                item.role = role
                                item.key = tag

                                # self._populate_item(item)
                                if tag not in self._all_items.keys():
                                    self._all_items[tag] = item.get_obj()

                                # if already in all tags, check if its from the same role
                                # if not, add to duplicate
                                elif role != self._all_items[tag]["role"]:
                                    if tag not in self._duplucate_items.keys():
                                        self._duplucate_items[tag] = []
                                        self._duplucate_items[tag].append(self._all_items[tag])
                                    self._duplucate_items[tag].append(item.get_obj())

                                # per role
                                if role not in self._role_items.keys():
                                    self._role_items[role] = {}
                                if tag not in self._role_items[role].keys():
                                    self._role_items[role][tag] = item.get_obj()

                    except yaml.YAMLError as exc:
                        print(exc)

    @staticmethod
    def find_tag(key,data):

        r = []
        if isinstance(data,list):
            for d in data:
                tmp_r = Annotation.find_tag(key, d)
                if tmp_r:
                    r = Annotation.merge_list_no_duplicates(r,tmp_r)

        elif isinstance(data,dict):
            for k,d in data.items():
                if k == key:
                    if isinstance(d,str):
                        d = [d]
                    r = r + d
                else:
                    tmp_r = Annotation.find_tag(key, d)
                    if tmp_r:
                        r = Annotation.merge_list_no_duplicates(r,tmp_r)
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