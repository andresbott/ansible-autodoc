# ansible-autodoc

[![CircleCI](https://circleci.com/gh/AndresBott/ansible-autodoc/tree/master.svg?style=svg)](https://circleci.com/gh/AndresBott/ansible-autodoc/tree/master)

Generate documentation from annotated playbooks and roles using templates.

    Note: this project is currently in Beta, issues, ideas and pull requests are welcome.

# Features
* allow to document playbook projects and roles
* use templates to generate and maintain the documentation
* extended functions when documenting:
   * tags: the autodoc will search for used tags in the project

# Getting started

```
# install 
pip install ansible-autodoc

# print help 
ansible-autodoc -h 

# print parsed annotation results in the cli 
ansible-autodoc -p all path/to/role_or_playbook 

# generate README file based on annotations  
ansible-autodoc [path/to/project] 
``` 

notes: 
* you can use [grip](https://pypi.org/project/grip/) to see the live changes.
* this only runs with python 3, if you still have python 2.x use pip3


# Annotations

Use the following annotations in your playbooks and roles

* __meta:__ use @meta to annotate the metadata of playbook or role, like author
check below list of useful metadata
  * author: (self explanatory)
  * description: playbook / role description
  * name: to define a different role/project name instead of the folder name
  * license: (self explanatory)
  * email: (self explanatory)
  
```yaml
# @meta author: Author Name
# @meta description: Project description
```  
* __todo:__ use @todo to annotate improvements, bugs etc
```yaml
# @todo bug: bug description
# @todo improvement: improvement 
```

* __action:__ use @action to annotate a actions performed by the playbook/role
```yaml
# @action install # this action describes the installation  
# @action # this action does not have a section, only description 
```

* __tags:__ use @tag to annotate tags, this is a special annotation as this will not only search for annotations,
but also for used tags in the project and add that to the generated output.
```yaml
# @tag tagname # tag description   
```


* __variables:__ use @var this to annotate configuration variables
```yaml
# @var my_var: default_value # description of the variable   
```

* __example:__ the idea is that after every annotation, we can define an example block, linked to the annotation.
in this case the example will be part of the var annotation.
```yaml
# @var my_var: default_value # description of the variable   
my_var: default_value
# @example # the hash is needed due to the parser constrains
# my_var:
#  - subitem: string
#  - subitem2: string
# @end
``` 

# Templates

ansible-autodoc comes with 3 templates out of the box, the default is "readme", you can change this in configuration.

If you want to create your own project specific templates, see the [template documentation](doc/templates.md)

If a file already exists in the output, the you will be prompted to overwrite or abort.

### README

The default "readme" template will generate a README.md file in the root of the project, detailing the sections:

* title and description
* actions
* tags
* variables
* todos
* license
* author infomration

you can extend this my creating a file `"_readme_doby.md"` in the root of your project, this will be included in the rendered Readme just after the 
initial description.

### Doc and README

The "doc_and_readme" template is an extended template intended to be used playbook projects with several roles, it will generate a minimal
README.md file and a documentation subfolder "doc" with more detailed information.

you can extend this my creating a file `"_readme_doby.md"` in the root of your project, this will be included in the rendered Readme just after the 
initial description.
 
the files created in the documentation folder will cover: 

* tags: list all tags classified by roles
* variables: list all variables classified by roles
* todo: list all todo actions classified by roles
* report: provides a report of the project and useful information during development

you can extend the documentation in this folder, just keep in mind that generated files will be overwritten.


### Command line 

The "cliprint" template is used to display the content when you use the command line print parameter "-p"


## Configuration
you can create a configuration file "autodoc.config.yaml" in the root of your project in order to modify
several behaviours, see the sample config file for more details:

```$xslt
# role or project with playbooks
$ cd <project> 

# create sample configuration (optional) 
# you can pass the options as parameters too
$ ansible-autodoc --sample-doc > autodoc.config.yaml
```

