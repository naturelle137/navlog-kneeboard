# VFR nav log kneeboard template
# SPDX-License-Identifier: CC-BY-SA-4.0

PYTHON ?= python3

BUILD  := build
PDF    := $(BUILD)/NavLog-A4-3up.pdf
HTML   := $(BUILD)/navlog.html
SRC    := src/slip.html src/navlog.css tools/build.py

.PHONY: all check preview clean

all: $(PDF)

$(PDF): $(SRC)
	@$(PYTHON) tools/build.py

## check: assert the printed geometry matches what the README promises
check: $(PDF)
	@$(PYTHON) tools/check.py

## preview: regenerate the PNG shown in the README
preview: $(PDF)
	@tools/preview.sh

clean:
	@rm -f $(BUILD)/navlog.html $(BUILD)/*.pdf
