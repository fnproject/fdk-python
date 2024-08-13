RAW_VERSION=$(shell grep -m1 -Eo "[0-9]+\.[0-9]+\.[0-9]+" fdk/version.py)
FDK_VERSION=$(RAW_VERSION).$(BLD_NUMBER)$(shell echo $(BLD_BRANCH_SUFFIX) | tr - _)

.PHONY: set_fdk_version unit_test build_dist_package

set_fdk_version:
	echo "version: \"$(FDK_VERSION)\"" > $(BLD_INPUT_DIR)/buildOverrideVariables.conf
	echo "fdk_version=$(FDK_VERSION)" >> $(BLD_INPUT_DIR)/exportVariables.env

unit_test:
	yum install -y python3.11 python3.11-pip python3.11-wheel python3.11-setuptools
	python3.11 -m venv unit-test-env && . unit-test-env/bin/activate
	echo "Python Version"
	python3 --version
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	pip3 install tox
	tox -epep8  # Check for style guide violations if any
	tox -epy3.11 # Execute unit tests
	rm -rf unit-test-env

build_dist_package:
	echo "build version: \"$(FDK_VERSION)\"" > $(BLD_INPUT_DIR)/buildOverrideVariables.conf
	yum install -y python3.11 python3.11-pip python3.11-wheel python3.11-setuptools
	python3.11 -m venv .dist_pkg_venv && source .dist_pkg_venv/bin/activate
	echo "Python Version"
	python3 --version
	pip3 install --upgrade pip
	pip3 install wheel
	# use latest setuptools to include License-File Key in Metadata file inside wheel pkg.
	pip3 install setuptools>=65.7.0
	PBR_VERSION=$(FDK_VERSION) python3 setup.py sdist bdist_wheel
	mv dist/fdk-*.tar.gz dist/fdk-$(FDK_VERSION).tar.gz
	rm -rf .dist_pkg_venv

set_image_version:
	echo "version: \"$(PYTHON_VERSION)-$(FDK_VERSION)$(if $(VERSION_SUFFIX),-$(VERSION_SUFFIX),)\"" > $(BLD_INPUT_DIR)/buildOverrideVariables.conf

setup_test_image_build:
    # Build tag for the test image
	echo "version: \"python-$(PYTHON_VERSION)-$(FDK_VERSION)\"" >$(BLD_INPUT_DIR)/buildOverrideVariables.conf
	echo "fdkVersion: \"$(FDK_VERSION)\"" >>$(BLD_INPUT_DIR)/buildOverrideVariables.conf
	echo "buildImageVersion: \"$(PYTHON_VERSION)-$(FDK_VERSION)-dev\"" >>$(BLD_INPUT_DIR)/buildOverrideVariables.conf
	echo "runtimeImageVersion: \"$(PYTHON_VERSION)-$(FDK_VERSION)\"" >>$(BLD_INPUT_DIR)/buildOverrideVariables.conf
	cat $(BLD_INPUT_DIR)/buildOverrideVariables.conf
	find $(BLD_INPUT_DIR)/internal/tests-images -name 'requirements.txt' -exec sh -c 'cp "dist/fdk-$(FDK_VERSION)-py3-none-any.whl" "$$(dirname {})"' \;
	find $(BLD_INPUT_DIR)/internal/tests-images -name 'requirements.txt' -exec sh -c 'cp "dist/fdk-$(FDK_VERSION).tar.gz" "$$(dirname {})"' \;