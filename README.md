# Nand2Tetris_JackCompiler

**NOTE:** If input jack files contain no syntax error, please use `simplified` branch for better performance.

This compiler is the project 11 of nand2tetris course. JackCompiler compiles *.jack files to *.vm files,
which is the virtual machine language used in nand2tetris course.

JackCompiler may compile single *.jack file or the all *.jack files in a directory.

## Requirements
Python 3.6+

## How to use:
Run:
```bash
python JackCompiler.py path
```
* `path`  Accept both directory and single filename.

*.vm file will be genarated in the same directory. 

**NOTE:** *.xml files are the by-product during the compiling. 

## Version Log
### 1.0 
  1. Complete basic function.

## TODO
* Remove the XML component. (maybe)
* Refactor redundant code.

（然而大概率是要摸了, RUA）

