### Compilation/Linking Tools and Flags ###

PYTHON = python
PYTHON_FLAGS = 

### Project Files and Directories ###

PROJ_DIR = .
IN_DIR = $(PROJ_DIR)/img
OUT_DIR = $(PROJ_DIR)/out

PROJ_MAIN = $(PROJ_DIR)/spa.py

### Build Rules ###

.PHONY : main

all : main

main : $(PROJ_MAIN) | $(OUT_DIR)
	$(PYTHON) $(PYTHON_FLAGS) $<

$(OUT_DIR) :
	mkdir $@

clean :
	rm -rf $(PROJ_DIR)/*.pyc $(OUT_DIR)
