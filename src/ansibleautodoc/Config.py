#!/usr/bin/env python3
import os
import yaml
from ansibleautodoc.Utils import Singleton


class Config:
    sample_config = """---
# About Ansible autodoc: Generate documentation from annotated playbooks and roles using templates
# https://github.com/AndresBott/ansible-autodoc
# filename: autodoc.conf.yaml

# base directoy to scan, relative dir to configuration file 
# base_dir: "./" 

# documentation output directory, relative dir to configuration file.
output_dir: "./doc" 

# directory containing templates, relative dir to configuration file, 
# comment to use default build in ones
# template_dir: "./template" 

# template directory name within template_dir
# build in "doc_and_readme" and "readme"
template: "readme" 

# Overwrite documentation pages if already exist
# this is equal to -y
# template_overwrite : False

# set the debug level: trace | debug | info | warn
# see -v | -vv | -vvv
# debug_level: "warn"

# when searching for yaml files in playbook projects, 
# excluded this paths (dir and files) from analysis 
# default values
excluded_playbook_dirs:
    - "host_vars"
    - "group_vars"
    - "host_secrets"
    - "plugins"
    - "autodoc.conf.yaml"
    
# when searching for yaml files in roles projects, 
# excluded this paths (dir and files) from analysis 
# default values
excluded_roles_dirs: []

"""
    # path to the documentation output dir
    output_dir = ""

    # project base directory
    _base_dir = ""

    # current directory of this object,
    # used to get the default template directory
    script_base_dir = ""

    # path to the directory that contains the templates
    template_dir = ""
    # default template name
    default_template = "readme"
    # template to use
    template = ""
    # flag to ask if files can be overwritten
    template_overwrite = False
    # flag to use the cli print template
    use_print_template = False

    # don't modify any file
    dry_run = False

    # default debug level
    debug_level = "warn"

    # internal flag
    is_role = None
    # internal when is_rote is True
    project_name = ""

    # name of the config file to search for
    config_file_name = "autodoc.conf.yaml"
    # if config file is not in root of project, this is used to make output relative to config file
    _config_file_dir = ""

    # directories and files excluded from scan
    excluded_playbook_dirs = [
        "host_vars",
        "group_vars",
        "host_secrets",
        "plugins",
        "autodoc.conf.yaml"
    ]

    excluded_roles_dirs = []

    # special Ansible tags to be removed from the tag list
    excluded_tags = [
        "always",
        "untagged",
        "never",
        "untagged",
    ]

    # used in self promotion
    autodoc_name= "Ansible-autodoc"
    autodoc_url= "https://github.com/AndresBott/ansible-autodoc"

    # annotation search patterns

    # for any pattern like ' # @annotation: [annotation_key] # description '
    # name = annotation ( without "@" )
    # allow_multiple = True allow to repeat the same annotation, i.e. @todo
    # automatic = True this action will be parsed based on the annotation in name without calling the parse method

    annotations = {
        "tag": {
            "name": "tag",
            "special":True
        },
        "meta": { # @meta: author # <name>
            "name": "meta",
            "automatic":True
        },
        "todo": {
            "name": "todo",
            "allow_multiple": True,
            "automatic": True,
        },
        "action": {
            "name": "action",
            "allow_multiple": True,
            "automatic": True,
        },
        "var": {
            "name": "var",
            "automatic": True,
        },
        "example": {
            "name": "example",
            "regex": "(\#\ *\@example\ *\: *.*)"
        },
    }

    def __init__(self):
        self.script_base_dir = os.path.dirname(os.path.realpath(__file__))

    def set_base_dir(self,dir):
        self._base_dir = dir
        self._set_is_role()

    def get_base_dir(self):
        return self._base_dir

    def get_annotations_definition(self, automatic=True,special=True):
        annotations = {}

        if automatic:
            for k, item in self.annotations.items():
                if "automatic" in item.keys() and item["automatic"]:
                    annotations[k]=item
        if special:
            for k, item in self.annotations.items():
                if "special" in item.keys() and item["special"]:
                    annotations[k]=item

        return annotations

    def get_annotations_names(self,automatic=True,special=False):

        annotations = []

        if automatic:
            for k, item in self.annotations.items():
                if "automatic" in item.keys() and item["automatic"]:
                    annotations.append(k)

        if special:
            for k, item in self.annotations.items():
                if "special" in item.keys() and item["special"]:
                    annotations.append(k)

        return annotations

    def _set_is_role(self):
        # is role
        self.project_name = os.path.basename(self._base_dir)
        if os.path.isdir(self._base_dir+"/roles"):
            self.is_role = False
        elif os.path.isdir(self._base_dir+"/tasks"):
            self.is_role = True
        else:
            self.is_role = None

    def get_output_dir(self):
        """
        get the relative path to cwd of the output directory for the documentation
        :return: str path
        """
        if self.use_print_template:
            return ""
        if self.output_dir == "":
            return os.path.realpath(self._base_dir)
        elif os.path.isabs(self.output_dir):
            return os.path.realpath(self.output_dir)
        elif not os.path.isabs(self.output_dir):
            return os.path.realpath(self._config_file_dir+"/"+self.output_dir)

    def get_template_base_dir(self):
        """
        get the base dir for the template to use
        :return: str abs path
        """
        if self.use_print_template:
            return os.path.realpath(self.script_base_dir+"/templates/cliprint")

        if self.template == "":
            template = self.default_template
        else:
            template = self.template

        if self.template_dir == "":
            return os.path.realpath(self.script_base_dir+"/templates/"+template)
        elif os.path.isabs(self.template_dir):
            return os.path.realpath(self.template_dir+"/"+template)
        elif not os.path.isabs(self.template_dir):
            return os.path.realpath(self._config_file_dir+"/"+self.template_dir+"/"+template)

    def load_config_file(self, file):

        allow_to_overwrite = [
            "base_dir",
            "output_dir",
            "template_dir",
            "template",
            "template_overwrite",
            "debug_level",
            "excluded_playbook_dirs",
            "excluded_roles_dirs",

        ]
        # overwrite_map = {
        #     "base_dir":"set_base_dir",
        # }

        with open(file, 'r') as yaml_file:

            try:
                self._config_file_dir = os.path.dirname(os.path.realpath(file))
                data = yaml.load(yaml_file)
                if data:
                    for item_to_configure in allow_to_overwrite:
                        if item_to_configure in data.keys():
                            self.__setattr__(item_to_configure,data[item_to_configure])

            except yaml.YAMLError as exc:
                print(exc)


class SingleConfig(Config, metaclass=Singleton):
    pass

