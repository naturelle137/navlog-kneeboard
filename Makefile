# VFR nav log kneeboard template
# SPDX-License-Identifier: CC0-1.0

PYTHON ?= python3

BUILD  := build
# Two variants, same outer size: 7L is seven legs with tighter rows, 6L is six
# legs with roomier ones. Stamped on the sheet next to the ▲ TOP mark.
TAGS   := 7L 6L
PDFS   := $(foreach t,$(TAGS),$(BUILD)/NavLog-A4-3up-$(t).pdf)
SRC    := src/slip.html src/navlog.css tools/build.py

.PHONY: all check preview clean

all: $(PDFS)

$(PDFS): $(SRC)
	@$(PYTHON) tools/build.py

## check: assert the printed geometry matches what the README promises
check: $(PDFS)
	@$(PYTHON) tools/check.py

## preview: regenerate the PNG shown in the README
preview: $(PDFS)
	@tools/preview.sh

clean:
	@rm -f $(BUILD)/navlog*.html $(BUILD)/*.pdf
