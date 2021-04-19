CHANGES
=======

0.1.23
------

* FDK Python: 0.1.23 release [skip ci]
* Added license files to wheel

0.1.22
------

* FDK Python: 0.1.22 release [skip ci]
* Add support for Oracle Cloud Infrastructure tracing solution by providing a tracing context #117
* Add support for Oracle Cloud Infrastructure tracing solution by providing a tracing context
* - Added versions 3.7 and 3.8 to FDK - Added scripts to build images properly

0.1.21
------

* FDK Python: 0.1.21 release [skip ci]

0.1.20
------

* FDK Python: 0.1.20 release [skip ci]
* Fix dependency issue with python 3.6.0

0.1.19
------

* FDK Python: 0.1.19 release [skip ci]
* Updated copyright headers, added NOTICE.txt and updated THIRD\_PARTY\_LICENSES.txt
* Set root logger to DEBUG to preserve existing log level behaviour
* Format logs with call ID and one-line exceptions
* Moved FDK logging to debug, and turned debug off by default
* Updated README.md

0.1.18
------

* FDK Python: 0.1.18 release [skip ci]
* Fix "None-None" race condition with keep-alive timeout

0.1.17
------

* FDK Python: 0.1.17 release [skip ci]
* Satisfy pep8 warnings
* Add Python 3.8.5

0.1.16
------

* FDK Python: 0.1.16 release [skip ci]
* Support sending response as binary data

0.1.15
------

* FDK Python: 0.1.15 release [skip ci]
* Refresh the Python FDK dependencies to more recent versions

0.1.14
------

* FDK Python: 0.1.14 release [skip ci]
* Fix issue with header prefixes, remove ambiguous header processing, add test

0.1.13
------

* FDK Python: 0.1.13 release [skip ci]
* Add third party license file

0.1.12
------

* FDK Python: 0.1.12 release [skip ci]
* Turn off CircleCI docker layer caching

0.1.11
------

* FDK Python: 0.1.11 release [skip ci]
* Pin attrs==19.1.0 as just released attrs 19.2.0 is breaking pytest https://github.com/pytest-dev/pytest/issues/5901
* fix formatting issues
* fix value of fn-fdk-version to include the fdk language. format: fdk-python/x.y.z
* ensure workflow works
* Ensure that CI pipeline works
* Fix request URL and HTTP method definitions
* Adding necessary git config vars to do commits from inside of the CI jobs (#93)
* Enable docker images release (#92)
* Fixing version placement command
* properly grab content type (#90)
* Disable image release procedure temporarily (#89)

0.1.6
-----

* FDK Python: 0.1.6 release [skip ci]
* fix gateway headers / headers casing (#88)
* removing corresponding TODO
* adding FDK release into the CI
* New PBR release broke setup config
* Automated releases + FDK version header (#82)
* attempt fixing content type issue (#83)
* Adding Anchore CI check (#77)
* If enabled, print log framing content to stdout/stderr (#81)
* Add fn user/group to 3.6 runtime image (#79)
* Runtime image updated: fn user/group fix
* Bring all Dockerfiles for supported Python runtimes into FDK repo (#76)
* fn user added to runtime image
* Make gen script add build/run images into func.yaml (#73)
* Script to generate and deploy a function from FDK git branch (#72)
* Adding Py3.5.2+ support (#70)
* changing request header fields in context to lower case (#67)
* Comply with internal Fn response code management (#65)
* Fix setuptools classfier reference
* asyncio + h11 (was #58) (#60)
* cleaning up code samples
* Removing application's code
* No py2 builds (#57)
* Requirements update (#56)
* Fixing unit test section in README (#55)
* Fn applications, request content reading fix (#54)
* HTTP stream format support (#51)
* Feature: unittest your function (#47)
* Fix protocol key addressing (#46)
* Moving docker images to FDK repo as officially supported (#45)
* Error handling improvement: default error content type to  application/json
* Improvement: make FDK return valid raw XML/HTML content (#42)
*  GoLikeHeaders.set() logic improvements (#41)
* Adjust parser to make fn-test fn-run at least spit out the response (#40)
* Refactoring. CloudEvents (#39)
* Fix headers rendering (#38)
* Hotfix: str -> bytes
* Try to identify the end of th request (#35)
* More debug information (#34)
* Stable parser! (#33)
* Fn-powered applications improvements (#32)
* Making fn-powered apps API stable (#31)
* General improvements (#30)
* Get rid of unstable coroutines (#29)
* Attempt to create new loop for each request
* Trying to fix the event loop access
* Use deadlines for coroutines
* Playing with an executor
* More logging
* Coroutine hotfix (#28)

v0.0.12
-------

* Do not attempt to jsonify response data (#27)

v0.0.11
-------

* Run coroutines thread-safely (#26)
* +x mode for release script
* Fix script name
* Update release script
* Coroutine support (#25)

v0.0.9
------

* Custom response objects (#24)
* New JSON parser! (#22)
* More wise JSON parsing with en empty body (#21)

v0.0.7
------

* Check the request body before trying to turn that into a json (#20)

v0.0.6
------

* New JSON protocol improvements (#19)

v0.0.5
------

* FDK Context| deadline | generic response, etc. (#16)
* Fix pytest capture (#12)
* Stable v0.0.4 release (#11)

v0.0.4
------

* Updating to newer JSON protocol (#10)
* Fixing release doc (#9)
* Stable v0.0.3 release (#8)
* Fn-powered truly-serverless apps with functions (#7)

v0.0.2
------

* Stable release v0.0.2 (#6)
* Applications powered by Fn (#5)
* Fixing root Dockerfile
* Updating samples deps to fdk-0.0.1

v0.0.1
------

* Fixing CircleCI again
* Fixing CircleCI config
* Adding circle CI config
* Attempting to pick appropriate binary
* Updating tox config for CircleCI
* Updating artifact name
* Refactoring to be a single handler based on FN\_FORMAT
* Get rid of verbose response in favour of http lib
* Implementing generic handler based on FN\_FORMAT
* Updating sample apps
* Updating root Dockerfile
* JSON parser added
* Addressing review comments
* Initial commit
* Initial commit
