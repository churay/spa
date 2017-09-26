### Compilation/Linking Tools and Flags ###

PYTHON = python
PYTHON_FLAGS = 

### Project Files and Directories ###

PROJ_DIR = .
PROJ_MAIN = $(PROJ_DIR)/spa.py

### Build Rules ###

.PHONY : main

all : main

main : $(PROJ_MAIN)
	$(PYTHON) $(PYTHON_FLAGS) $<

clean :
	rm -rf $(PROJ_DIR)/*.pyc $(OUT_DIR)
