#!/usr/bin/python3
import yaml
import os



class Utils:
    # class TerminalColors:
    #     HEADER = '\033[95m'
    #     OKBLUE = '\033[94m'
    #     OKGREEN = '\033[92m'
    #     WARNING = '\033[33m'
    #     FAIL = '\033[91m'
    #     ENDC = '\033[0m'
    #     BOLD = '\033[1m'
    #     UNDERLINE = '\033[4m'

    class term_colors:
        '''Colors class:reset all colors with colors.reset; two
        sub classes fg for foreground
        and bg for background; use as colors.subclass.colorname.
        i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable,
        underline, reverse, strike through,
        and invisible work with the main class i.e. colors.bold'''
        reset='\033[0m'
        bold='\033[01m'
        disable='\033[02m'
        underline='\033[04m'
        reverse='\033[07m'
        strikethrough='\033[09m'
        invisible='\033[08m'
        class fg:
            black='\033[30m'
            red='\033[31m'
            green='\033[32m'
            orange='\033[33m'
            blue='\033[34m'
            purple='\033[35m'
            cyan='\033[36m'
            pink='\033[95m'
            yellow='\033[93m'
            lightgrey='\033[37m'
            darkgrey='\033[90m'
            lightred='\033[91m'
            lightgreen='\033[92m'
            lightblue='\033[94m'
            lightcyan='\033[96m'
        class bg:
            black='\033[40m'
            red='\033[41m'
            green='\033[42m'
            orange='\033[43m'
            blue='\033[44m'
            purple='\033[45m'
            cyan='\033[46m'
            lightgrey='\033[47m'

    @staticmethod
    def removeNonAscii(s):
        r = "".join(i for i in s if ord(i) < 128)
        r = r.replace("/", "_")
        r = r.replace("\"", "")
        r = r.replace("\'", "")
        return r

    @staticmethod
    def remove_line_modif(s):
        r = s.replace("\n", "")
        r = r.replace("\t", "")
        return r

    @staticmethod
    def escape_string(s):
        # https://stackoverflow.com/questions/18935754/how-to-escape-special-characters-of-a-string-with-single-backslashes
        return s.translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "\"":  r'\"',
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\."}))

    @staticmethod
    def remove_dup_spaces(s):
        return " ".join(s.split())

    @staticmethod
    def load_yaml(file, default=None):
        if not os.path.isfile(file):
            return None

        with open(file, 'r') as stream:
            try:
                c = yaml.load(stream)
                if default is not None:
                    return Utils.merge_objects(default,c)
                    # for item in default:
                    #     if c.get(item) is not None:
                    #         default[item] = c.get(item)
                    # return default
                else:
                    return c

            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def merge_objects(default,value):
        for item in default:
            if value.get(item) is not None:
                default[item] = value.get(item)
        return default


    @staticmethod
    def create_path(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def write_yaml(file, content):
        with open(file, 'w') as outfile:
            yaml.dump(content, outfile, default_flow_style=False, allow_unicode=True)

    @staticmethod
    def write_file(file, content):
        file = open(file, "w")
        file.write(content)
        file.close()

    @staticmethod
    def read_file(file):
        file = open(file, "r")
        return file.read()

    @staticmethod
    def read_csv(file, separator=","):
        obj = {
            "head": [],
            "data": []
        }

        lines = open(file, 'r').readlines()
        if len(lines) > 0:

            head_line = lines[0].split(separator)
            for i in head_line:
                t = i.strip()
                t = Utils.remove_line_modif(t)
                if t != "":
                    obj["head"].append(t)
            lines.pop(0)

        if len(lines) > 0:
            for line in lines:
                base = {}

                line_data = line.split(separator)
                for h in obj["head"]:
                    h_idnex = obj["head"].index(h)
                    if (len(line_data) - 1) >= h_idnex:
                        data_item = line_data[h_idnex]
                        data_item = data_item.strip()
                        data_item = Utils.remove_line_modif(data_item)
                    else:
                        data_item = ""

                    base[h] = data_item
                obj["data"].append(base)
        return obj

    @staticmethod
    def write_csv(file, data, separator=","):
        file = open(file, "w")

        head = data["head"]
        head = str(separator).join(head)
        file.write(head+"\n")

        body = data["data"]
        for line in body:
            line_data =[]
            for h in data["head"]:
                line_data.append(str(line[h]))

            line_data = str(separator).join(line_data)
            file.write(line_data+"\n")

        file.close()


    @staticmethod
    def read_last_line_of_file(file):
        with open(file, 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            return last_line


    @staticmethod
    def replace_spaces(s, rep="_", lower=False):

        # list
        if isinstance(s, list):
            for i in s:
                Utils.replace_spaces(s, rep, lower)

        # string
        elif isinstance(s, str):
            s = s.replace(" ", rep)
            if lower is True:
                s = s.lower()

        return s