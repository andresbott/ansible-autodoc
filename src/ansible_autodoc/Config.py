#!/usr/bin/env python3
import os
from ansible_autodoc.Utils import Singleton


class Config:

    output_dir = ""
    base_dir = ""
    script_base_dir = ""
    template_dir = ""
    template = "doc_and_readme"
    template_overwrite = False
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
        self.script_base_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.realpath(self.script_base_dir+"/../templates/"+self.template)


class SingleConfig(Config, metaclass=Singleton):
    pass

