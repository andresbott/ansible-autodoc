#!/usr/bin/env python3
from utils.singleton import Singleton

class Config:

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

class SingleConfig(Config,metaclass=Singleton):
    pass

