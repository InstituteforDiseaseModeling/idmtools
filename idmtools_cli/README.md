![Staging: idmtools-cli](https://github.com/InstituteforDiseaseModeling/idmtools/workflows/Staging:%20idmtools-cli/badge.svg?branch=dev)

# idmtools-cli

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

  - [Installing](#installing)
- [Development tips](#development-tips)
- [Using the CLI](#using-the-cli)
  - [Version command](#version-command)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installing

```bash
pip install idmtools-cli
```

# Development tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
lint        -   Lint package and tests
test        -   Run All tests
coverage    -   Run tests and generate coverage report that is shown in browser
```
On Windows, you can use `pymake` instead of `make`

# Using the CLI

`idmtools --help`

## Version command

To determine version of idmtools and related plugins, use the version cli command.


```
idmtools version
```

Example output
```bash
emodpy                               Version: 1.3.0                          
  Plugins:
    EMODTask                  
idmtools                             Version: 3.1.0                 
  Plugins:
    CommandTask               
idmtools-cli                         Version: 3.1.0                
idmtools-models                      Version: 3.1.0                 
  Plugins:
    JSONConfiguredPythonTask  
    JSONConfiguredRTask       
    JSONConfiguredTask        
    PythonTask                
    RTask                     
    ScriptWrapperTask         
    TemplatedScriptTask       
idmtools-platform-comps              Version: 3.1.0                
  Plugins:
    COMPSPlatform             
    SSMTPlatform                        
idmtools-platform-slurm              Version: 3.1.0                  
  Plugins:
    SlurmPlatform             
```

