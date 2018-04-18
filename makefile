### Compilation/Linking Tools and Flags ###

PYTHON = python
PYTHON_FLAGS = 

### Project Files and Directories ###

PROJ_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SRC_DIR = $(PROJ_DIR)/spa
EX_DIR = $(PROJ_DIR)/ex
IN_DIR = $(PROJ_DIR)/in
OUT_DIR = $(PROJ_DIR)/out

PROJ_MAIN = $(PROJ_DIR)/spa.py

### Build Rules ###

.PHONY : %.ex clean

%.ex : $(EX_DIR)/%.py | $(OUT_DIR)
	$(PROJ_MAIN) -v -o $(subst .ex,.mp4,$@) $<

$(OUT_DIR) :
	mkdir $@

clean :
	rm -rf $(PROJ_DIR)/*.pyc $(SRC_DIR)/*.pyc $(OUT_DIR)
	find . -name "*.mp4" -exec rm -f {} \;
