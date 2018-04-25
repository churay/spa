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

.PHONY : clean

%.mp4 : $(EX_DIR)/%.py $(wildcard $(SRC_DIR)/*.py) | $(OUT_DIR)
	$(PROJ_MAIN) -e mp4 -v -o $(subst .ex,.mp4,$@) $<

%.gif : $(EX_DIR)/%.py $(wildcard $(SRC_DIR)/*.py) | $(OUT_DIR)
	$(PROJ_MAIN) -e gif -v -o $(subst .ex,.gif,$@) $<

$(OUT_DIR) :
	mkdir $@

clean :
	rm -rf $(PROJ_DIR)/*.pyc $(SRC_DIR)/*.pyc $(OUT_DIR)
	find . \( -name "*.mp4" -o -name "*.gif" \) -exec rm -f {} \;
