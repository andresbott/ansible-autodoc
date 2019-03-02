# Templates

A template consists of a folder that contains a set of jinja2 files with .j2 extension.

This folder will be used as blueprint to genereate the documentation output, meaning that every file that does NOT begin
with "_" will be rendered using jinja and placed in the destination.

for example a template structure like this

    ./Readme.md.j2
    ./docs/variables.md.j2
    ./docs/_helper.md.j2

will render as 

    ./Readme.md
    ./docs/variables.md
    
Once you have created your folder the will become your template, you can specify in the configuration file to 
use this as template.

## Annotation parsing

Annotations are parsed as follows: `@annotation key:value # description`
your annotation item would then contain these values and some automatically filled data (if available):
```
{
  "key": "key section",
  "value": "value section",
  "desc": "description",
  "file": "path where the annotation was found",
  "line": "line number of the annotation",
  "role": "name of the role the annotation was found"
}
```


## Template API
when templating autodoc projects you will have the methods from DocumentParser exposed in the templates:
'r' is a reference to the parser in order to do things like:
```
{{ r.get_roles() | pprint }}
```

* r.get_gata() : get the full data of autodoc in jason structure, this can be quite overwhelming when templating
* r.get_annotations() : get a list of the scanned annotations as per configuration
* r.get_roles(exclude_playbook) : return a list of scanned roles, if exclude_playbook is True the palybook 
role '_ansible_playbook_' is removed
* r.is_role() : return True if the scanned project directory is identified as role, false if scanned as playbook
* r.get_role_name() : If scanned project is a role, return role name (project folder name)
* r.get_type(name,role="all"): return an array with the corresponding annotation "name", role is optional
  * if "all" or not specified, the mixed result for all roles will be returned
  * if "play" specified, the playbook results will be returned
* r.get_multi_type(name,role="all"): return a dict of all the annotations with structure `section:[item1,item2]`
you can use it like:
``` 
{% for key , values in r.get_multi_type("action","role_name") %}
    {{ key }}
    {% for item in values %}
        {{ item.desc }}
    {% endfor %}
{%  endfor %}
```  
* r.get_keys(name,role="all"): return a list of annotation keys, same parameters as get_type.
* r.get_item(name,key,role="all"): return a single annotation item, same parameters as get_type plus "key"
* r.get_duplicates(name): return a dict of annotations that are duplicated, i.e useful for tags to identify 
if they have been annotated more than once or if there are tags used in more than one role.
* r.allow_multiple(name): check if a annotation allows multiple values, like @todo or @action.
* r.include(filename): include a tex file, path relative to the project root 

* r.cli_left_space("string",spaces) : left justify with spaces a string, spaces is optional, see python ljust()
* r.cli_print_section() : return the passed parameter when using cli print "-p", default is "all"

* r.capitalize(string) : wrapper for python capitalize
* r.fprn(role_name,replace_value="Playbook"): "filter playbook role name" replace the internal playbook role name 
"_ansible_playbook_" with a different value.