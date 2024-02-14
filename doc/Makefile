# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    = -j auto --color
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Customized clean
clean:
	rm -rf $(BUILDDIR)/*

# Build html docs in parallel using all available CPUs
html:
    @$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -j auto

# Build pdf docs.
pdf:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/pyaedt-examples.pdf && echo pdf exists) || exit 1
