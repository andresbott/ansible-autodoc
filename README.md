# ansible-autodoc
Generate documentation from annotated playbooks and roles using templates

# Features
* allow to document playbook projects and roles
* use templates to generate and maintain the documentation
* extended functions when documenting:
   * tags: the autodoc will search for used tags in the project

# Installation
## Manual
1. download / git clone this project 
2. run `install.py` Note sudo is required

## Pip
using pip
```
pip install ansible-autodoc
``` 

# Use

## Annotations

Use the following annotations in your playbooks and roles

* tags: `# @tag tagname : description` to annotate tags
* author: `# @author Author Name` to annotate the author of playbook or role
* description: `# @description Project description goes here` to annotate the project description
* todo: `# @todo Taskt that need to be done` to annotate a todo

### Not implemented:
this is still not implemented, just an idea
* Role Variables `# @var[group] var_name : variable description` to annotate a variable
  how to add multi line example? match # @example:  and finish on the next linie that does not 
  start with # 


## Generate Documentation

```$xslt
# role or project with playbooks
$ cd <project> 

# create sample configuration (optional) 
# you can pass the options as parameters too
$ ansible-autodoc --sample-doc > autodoc.config.yaml

# crate documentation
$ ansible-autodoc 

# more options
$ ansible-autodoc -h
```

# Templates
the template engine uses jinja2 for document parsing, the directory structure of the template
will be recreated on the output, already existent files will be overwritten.

you can specify your own template, for extending templates create a new template directory and 
specify the location of the same in the configuration file.

 
# changelog 
2019/01/20 - Version 0.4.0
  * Basic functionality with tags working


# Build
clean:
`./setup.py clean --all`

build `./setup.py sdist [bdist_wheel]`

upload `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`