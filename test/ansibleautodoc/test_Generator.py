#!/usr/bin/python3
import os

from ansibleautodoc.Config import SingleConfig
from ansibleautodoc.DocumentationGenerator import Generator
from ansibleautodoc.DocumentationParser import MocParser

project_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../../")
sample_project = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../test-project")


class TestGenerator(object):

    def test_scan_template(self,tmpdir):

        config = SingleConfig()
        config.template_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../")
        config.template = "test-template"
        doc_generator = Generator({})
        print(doc_generator.template_files)
        assert doc_generator.template_files == ['Readme.md.j2', 'sub_dir/_sample_include.md.j2', 'sub_dir/subdir.md.j2']

    def test_render(self,tmpdir):
        config = SingleConfig()
        config.template_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../")
        config.template = "test-template"
        config.output_dir = str(tmpdir)+"/generated_doc"

        doc_parser = MocParser()
        doc_generator = Generator(doc_parser)

        doc_generator.render()

        rendered_file = open(str(tmpdir)+"/generated_doc/Readme.md", "r")
        line = rendered_file.read()

        print(line)
        # assert line == "Sample verification string"


