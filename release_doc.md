Release process
===============

Run tests on target brunch
--------------------------

Steps:

    tox

Cut off stable branch
---------------------

Steps:

    git checkout -b vX.X.X-stable
    git push origin vX.X.X-stable


Create GitHub tag
-----------------

Steps:

    Releases ---> Draft New Release
    Name: FDK-Python version X.X.X stable release


Collect changes from previous version
-------------------------------------

Steps:

    git log --oneline --decorate


Build distribution package
--------------------------

Steps:

    PBR_VERSION=X.X.X python setup.py sdist bdist_wheel


Check install capability for the wheel
--------------------------------------

Steps:

    virtualenv .test_venv -ppython3.6
    source .test_venv/bin/activate
    pip install dist/fdk-python-X.X.X-py2.py3-none-any.whl


Submit release to PYPI
----------------------

Steps:

    twine upload dist/fdk-X.X.X*

Verify install capability for the wheel
---------------------------------------

Steps:

    virtualenv .new_venv -ppython3.6
    source .new_venv/bin/activate
    pip install fdk-python --upgrade
