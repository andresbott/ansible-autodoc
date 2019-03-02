# Todo

list of documented items to change, solve or improve

## issues
* when a yaml file with a special char is templated, an UnicodeEncodeError will be thrown 
* Improve test coverage
* add template cli parameter

## improvements
* improve the default templates : ongoing task
* improve the documentation : ongoing task
* improve data extraction from annotations: '@example #' requires the # to identify the following lines as content
* add @autodoc tag, to use as flags for specific templates, i.e # @autodoc tags:hidden #
* add configuration file for defining template include locations, to allow to have multiple include files in a subfolder
to hide the render of tags section
* add annotation personalization by extending annotation definition in configuration file
* document annotation personalization
