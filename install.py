#!/usr/bin/python3

import os
import sys
import subprocess

class install():
    bin = [
        {
            "origin":"src/bin/ansible-autodoc",
            "dest":"ansible-autodoc-dev"
        },
    ]

    libs =[
        {
            "origin":"src/ansibleautodoc",
            "dest":"ansibleautodoc"
        },
    ]
    extra =[ ]


    def __init__(self):

        self.current_file_dir = os.path.dirname(os.path.abspath(__file__))
        self.dest_libs_dir = "/usr/lib/python3/dist-packages"
        self.dest_bin= "/usr/bin"
        self.user_home = os.environ["HOME"]
        self.dry = False

        if len(sys.argv) > 2:
            param = sys.argv[2]

            if param == "--dry":
                self.dry = True
            else:
                self.dry = False

        if len(sys.argv) > 1:
            param = sys.argv[1]

            if param == "--help" or param ==  "-h":
                self.print_help()
            elif param == "--install":
                self.install()
            elif param == "--uninstall":
                self.uninstall()
            else:

                self.print_help()
        else:
            self.print_help()

    def print_help(self):
        print("About: use install.py --<install | uninstall> --[dry]")
        print( "parameters: "+ str(sys.argv))

    def link_mod(self,file,type,action):
        ori = None
        dest = None

        # make a symlink in bin location
        if type == "bin":
            if "lib" in file.keys():
                ori = os.path.join(self.dest_libs_dir,  file["lib"])
            elif "origin" in file.keys():
                ori = os.path.join(self.current_file_dir,  file["origin"])

            dest = os.path.join(self.dest_bin, file["dest"])

        # make a symlink in python 3 libraries location
        if type == "lib":
            dest = os.path.join(self.dest_libs_dir, file["dest"])
            ori = os.path.join(self.current_file_dir,  file["origin"])

        # make other hardcoded links
        if type == "extra":
            dest = file["dest"]
            ori = os.path.join(self.current_file_dir,  file["origin"])


        if ori is not  None and dest is not None:

            if action == "add":
                cmd = "sudo ln -s "+ ori+ " "+ dest
            elif action == "rm":
                cmd = "sudo rm "+dest

            if self.dry is False:
                print(cmd)
                return_code = subprocess.call(cmd, shell=True)
            else:
                print("dry run: "+ cmd)


    def install(self):
        print("Install")
        for i in self.bin:
            self.link_mod(i,"bin","add")
        for j in self.libs:
            self.link_mod(j,"lib","add")
        for k in self.extra:
            self.link_mod(k,"extra","add")

    def uninstall(self):
        print("Uninstall")
        for i in self.bin:
            self.link_mod(i,"bin","rm")
        for j in self.libs:
            self.link_mod(j,"lib","rm")
        for k in self.extra:
            self.link_mod(k,"extra","rm")

if __name__ == "__main__":
    i = install()

