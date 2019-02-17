# ansible-autodoc
Generate documentation from annotated playbooks and roles using templates.

Note: this project is currently in Beta, issues, ideas and pull requests are welcome.

# Features
* allow to document playbook projects and roles
* use templates to generate and maintain the documentation
* extended functions when documenting:
   * tags: the autodoc will search for used tags in the project

# Installation
## Manual (for dev)
1. download / git clone this project
2. cd ansible-autodoc
3. `pip install -e ./`

## Pip
using pip
```
pip install ansible-autodoc
``` 

## Use
```$xslt
ansible-autodoc -h # print help
ansible-autodoc -p all path/to/role # print in cli all the recolected data 
ansible-autodoc [path/to/project] # will generate README file based on annotations  
``` 
### more flexibility 
you can create a configuration file "autodoc.config.yaml" in the root of your project in order to modify
several behaviours, see the sample config file for more details:

```$xslt
# role or project with playbooks
$ cd <project> 

# create sample configuration (optional) 
# you can pass the options as parameters too
$ ansible-autodoc --sample-doc > autodoc.config.yaml
```

# Annotations

Use the following annotations in your playbooks and roles

* meta: `# @meta author: Author Name` to annotate the metadata of playbook or role, like author, 
check below list of useful metadata
  * author: (self explanatory)
  * description: playbook / role description
  * name: to define a different role/project name instead of the folder name
  * license: (self explanatory)
  * email: (self explanatory)
* todo: `# @todo: section #Taskt that need to be done` to annotate a todo
* action: `# @action section # description of the action` to annotate a actions performed by the playbook/role
* tag: `# @tag tagname # description` to annotate tags, this is a special annotation as this will not only search
for annotations, but also for used tags in the project and add that to the generated output.
* variables: `# @var varname: ["some_defaut","other"] # Description of the variables` to annotate a variables
* example: the idea is that after every annotation, we can define an example block, linked to the annotation.
```$xslt
# @example: title # Some description
# here comes some 
# multi line block
# @end
``` 

## Not implemented:
this is still not implemented, just ideas 

`Nothing here`

# Templates
the template engine uses jinja2 for document parsing, the directory structure of the template
will be recreated on the output, already existent files will be overwritten.

you can specify your own template, for extending templates create a new template directory and 
specify the location of the same in the configuration file.

annotations are parsed as follows: "@annotation key:value # description"
your annotation item would then contain these values and some automatically filled if available:
```
{
  "key": "key section",
  "value": "value section",
  "desc": "description",
  "file": "absolute path where the annotation was found",
  "line": "line number of the annotation",
  "role": "name of the role the annotation was found"
}
```


## template API
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
 
# changelog

2019/02/17 - Version 0.5.2
  * FIX: run only in playbook or role project 
  * add -V | --version to cli
  * solve pip install issues

2019/02/17 - Version 0.5.1.1
  * add missing feature @example
  * improve default template "readme"
  * update install dependency on yaml for pip

2019/02/17 - Version 0.5.0
  * added uint tests
  * refactored annotation discovery into Annotation object
  * changed annotation to allow multi line description
  * made annotation syntax more uniform 
  * moved some essential logic from AutodocCli to Config
  * IMPROVEMENT: got rid of annotations author and description and use meta: author | description instead
  * Missing feature from 0.4: @example

2019/01/22 - Version 0.4.2
  * FIX: yaml load unicode files
  * FIX: document parsing when some annotations are not present 
  * improvements on the cli template
  
2019/01/21 - Version 0.4.2
  * Added example block annotation

2019/01/21 - Version 0.4.1
  * Added print template to stdout, useful for project review and development
  * Added @var annotation

2019/01/20 - Version 0.4.0
  * Basic functionality with tag annotations working
  * simple annotations: "author", "description" and "todo2 also working

# Todo
* when a yaml file with a special char is templated, an UnicodeEncodeError will be thrown 
* Improve test coverage
* add template cli parameter

### improvements
* improve the default templates : ongoing task
* improve the documentation : ongoing task
* add @autodoc tag, to use as flags for specific templates, i.e # @autodoc tags:hidden # 
to hide the render of tags section
* add annotation personalization by extending annotation definition in configuration file
* document annotation personalization

# Build
clean:
`./setup.py clean --all`

build `./setup.py sdist [bdist_wheel]`

upload `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`