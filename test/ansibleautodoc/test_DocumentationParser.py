#!/usr/bin/python3
import os

from ansibleautodoc.Config import SingleConfig

from ansibleautodoc.DocumentationParser import Parser


class TestDocumentationParser(object):

    def test_get_data(self):

        config = SingleConfig()
        doc_parser = Parser()
        print(doc_parser.get_data())
        # config.template_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"../../")
        # config.template = "test-template"
        # doc_generator = Generator({})
        # print(doc_generator.template_files)
        # assert doc_generator.template_files == ['Readme.md.j2', 'sub_dir/_sample_include.md.j2', 'sub_dir/subdir.md.j2']

