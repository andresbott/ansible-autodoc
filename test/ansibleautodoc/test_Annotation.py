#!/usr/bin/python3
import os
import pprint

from ansibleautodoc.Config import SingleConfig, Config
from ansibleautodoc.Annotation import Annotation
from ansibleautodoc.FileRegistry import Registry

project_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../../")
sample_project = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../test-project")

config = SingleConfig()
config.set_base_dir(sample_project)

fr = Registry()
fr._doc = {
    "_ansible_playbook_": [sample_project+"/test.yaml"],
    "role1":[sample_project+"/roles/role1/tasks/test.yaml"]
}

def test_get_details():
    print()
    annotation = Annotation("meta",files_registry=fr)

    items = annotation.get_details()

    item1 = items["all"]["key1"]
    assert item1["key"] == "key1"
    assert item1["value"] == "value1"
    assert item1["desc"] == ""

    item2 = items["all"]["key2"]
    assert item2["desc"] == "desc2"
    assert item2["value"] == "value2"

    item3 = items["all"]["key3 multi-word"]
    assert item3["key"] == "key3 multi-word"
    assert item3["desc"] == "value3 desc3"

    item4 = items["all"]["key4"]
    assert item4["value"] == ""
    assert item4["desc"] == "desc4 desc42"

def test_get_details_on_duplicates():
    print()
    annotation = Annotation("todo",files_registry=fr)

    items = annotation.get_details()

    cat1 = items["all"]["cat1"]

    found_desc = False
    found_desc2 = False
    for todo in cat1:
        if "desc1-1 desc1-1newline" == todo["desc"]:
            found_desc = True
        if "desc1-2 desc1-2newline" == todo["desc"]:
            found_desc2 = True
    if found_desc and found_desc2:
        assert True
    else:
        assert False

def test_get_details_on_tags():
    print()
    annotation = Annotation("tag",files_registry=fr)

    items = annotation.get_details()

    # pprint.pprint(items)