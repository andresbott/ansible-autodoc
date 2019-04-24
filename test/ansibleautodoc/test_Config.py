#!/usr/bin/python3
import os

from ansibleautodoc.Config import SingleConfig, Config

project_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../../")
sample_project = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../test-project")

def test_is_role():
    conf = SingleConfig()
    conf.set_base_dir(sample_project)
    assert conf.is_role == False
    conf.set_base_dir(os.path.realpath(sample_project+"/roles/role1"))
    assert conf.is_role == True

def test_default_template_dir():
    conf = Config()
    basedir = conf.get_template_base_dir()
    basedir = os.path.normcase(os.path.realpath(basedir)).replace("src","test")
    sample = os.path.normcase(os.path.realpath("ansibleautodoc/templates/readme"))
    assert basedir == sample

def test_get_annotation_definition():
    conf = Config()
    items = conf.get_annotations_definition(automatic=True)
    test_item = {'name': 'var', 'automatic': True}

    assert test_item == items["var"]
    assert "block_end" not in items.keys()

