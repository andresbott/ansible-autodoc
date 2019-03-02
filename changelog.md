# changelog

2019/02/17 - Version 0.5.3
  * FIX: when reporting files, use relative paths
  * improve readme template
  * improve doc_and_readme template

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
