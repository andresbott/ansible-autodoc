#!/usr/bin/env python3

import glob
import os
import sys

from ansible_autodoc.Utils import SingleLog,FileUtils
from ansible_autodoc.Config import SingleConfig
from jinja2 import Environment


class Generator:

    template_files = []
    extension = "j2"
    doc_data = None

    def __init__(self,doc_data):
        self.config = SingleConfig()
        self.log = SingleLog()

        self.log.trace("Documentation Generator")
        self.log.info("[Generator] Using template dir: "+self.config.template_dir)
        self.log.info("[Generator] Using output dir: "+self.config.output_dir)

        self.doc_data = doc_data

        self._scan_template()
        self._write_doc()


    def _scan_template(self):
        """
        Search for Jinja2 (.j2) files to apply to the destination
        :return: None
        """

        base_dir = self.config.template_dir

        for file in glob.iglob(base_dir+'/**/*.'+self.extension, recursive=True):

            relative_file = file[len(base_dir)+1:]
            self.log.trace("[GENERATOR] found template file: "+relative_file)
            self.template_files.append(relative_file)

    def _write_doc(self):
        files_to_overwite = []
        doc_data = self.doc_data

        os.makedirs(self.config.output_dir, exist_ok=True)

        for file in self.template_files:
            doc_file=self.config.output_dir+"/"+file[:-len(self.extension)-1]
            if os.path.isfile(doc_file):
                files_to_overwite.append(doc_file)

        if len(files_to_overwite) > 0 and self.config.template_overwrite is False:
            SingleLog.print("This files will be overwritten:",files_to_overwite)
            resulst = FileUtils.query_yes_no("do you want to continue?")
            if resulst != "yes":
                sys.exit()

        for file in self.template_files:
            doc_file = self.config.output_dir+"/"+file[:-len(self.extension)-1]
            source_file = self.config.template_dir+"/"+file

            self.log.trace("[GENERATOR] Writing doc output to: "+doc_file+" from: "+source_file)

            # make sure the directory exists
            os.makedirs(os.path.dirname(os.path.realpath(doc_file)), exist_ok=True)

            if os.path.exists(source_file) and os.path.isfile(source_file):
                with open(source_file, 'r') as template:
                    data = template.read()

                    if data is not None:
                        data = Environment(lstrip_blocks=True, trim_blocks=True).from_string(data).render(doc_data)

                        with open(doc_file, 'w') as outfile:
                            outfile.write(data)
