#!/usr/bin/python3
import os
from ansibleautodoc.FileRegistry import Registry
from ansibleautodoc.Config import SingleConfig,Config
from ansibleautodoc.Contstants import *

project_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../../")
sample_project = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../test-project")

def test_get_files():

    config = SingleConfig()
    config.set_base_dir(sample_project)
    file_registry = Registry()
    fr_items = file_registry.get_files()

    assert "_ansible_playbook_" in fr_items
    assert "role1" in fr_items

    assert_file = os.path.realpath(project_dir+"/test/test-project/test.yaml")
    assert assert_file in fr_items[PLAYBOOK_ROLE_NAME]

    assert_role_file = os.path.realpath(project_dir+"/test/test-project/roles/role1/tasks/test.yaml")
    assert assert_role_file in fr_items["role1"]
    print("")


def test_omitted_file():
    # logs = SingleLog()
    # logs.set_level("trace")

    config = Config()
    config.set_base_dir(sample_project)

    file_registry = Registry()
    fr_items = file_registry.get_files()
    assert_file = os.path.realpath(project_dir+"/test/sample-project/"+AUTODOC_CONF_FILE)
    assert assert_file not in fr_items[PLAYBOOK_ROLE_NAME]
