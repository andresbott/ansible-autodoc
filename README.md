# ansible-autodoc
Generate documentation from annotated playbooks and roles using templates

Please note this is still a work in progress, while the code might work in it's current state 
I don't recommend yet to use it, as I will probably change things.

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
using pip (not yet)
```
pip install ansible-autodoc
``` 

# Use

## Annotations

Use the following annotations in your playbooks and roles

* author: `# @author: Author Name` to annotate the author of playbook or role
* description: `# @description: Project description goes here` to annotate the project description
* todo: `# @todo: section #Taskt that need to be done` to annotate a todo
* tags: `# @tag: tagname # description` to annotate tags
* variables: `# @var: varname: ["some_defaut","other"] # Description of the variables` to annotate a variables

### Not implemented:
this is still not implemented, just an idea
* example: the idea is that after every annotation, we can define an example block, linked to the annotation.
```$xslt
# @example: title # Some description
# here comes some 
# multi line block
# @end
``` 


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
2019/01/21 - Version 0.4.1
  * Added print template to stdout, useful for project review and development
  * Added @var annotation


2019/01/20 - Version 0.4.0
  * Basic functionality with tag annotations working
  * simple annotations: "author", "description" and "todo2 also working


# Build
clean:
`./setup.py clean --all`

build `./setup.py sdist [bdist_wheel]`

upload `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`