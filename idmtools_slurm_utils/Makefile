
HTML_TEST_REPORT ?= slurm_utils.test_results.html
# Enable only parallel testing since cli has no serial tests
PARALLEL_TESTING = 1
include $(abspath ../../dev_scripts/test_root.mk)

help:
	help-from-makefile -f ../dev_scripts/package_general.mk -f ./Makefile