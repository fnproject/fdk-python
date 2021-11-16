#!/usr/bin/env bash
set -ex

declare -A versionLookup

#If any new dependencies are added to requirements.txt file, then this file needs an update to include those new dependencies
for FILE in ./fdk_dependencies/*.whl
do

    fileName=`echo $FILE`
    fileName=${fileName:19}
    idx=`expr index $fileName -`
    wheelFileName=${fileName:0:idx-1}
    wheelVersion=${fileName:$idx}
    idx=`expr index $wheelVersion -`
    wheelVersion=${wheelVersion:0:$idx-1}

    case $wheelFileName in
            pytest)  versionLookup[pytest]=`echo $wheelVersion` ;;
            pbr)  versionLookup[pbr]=`echo $wheelVersion` ;;
            iso8601)  versionLookup[iso8601]=`echo $wheelVersion`  ;;
            httptools)  versionLookup[httptools]=`echo $wheelVersion`  ;;
            zipp)  versionLookup[zipp]=`echo $wheelVersion`  ;;

            wcwidth) versionLookup[wcwidth]=`echo $wheelVersion` ;;
            typing_extensions)  versionLookup[typing_extensions]=`echo $wheelVersion` ;;
            pyparsing)  versionLookup[pyparsing]=`echo $wheelVersion`  ;;
            py)  versionLookup[py]=`echo $wheelVersion`  ;;
            pluggy)  versionLookup[pluggy]=`echo $wheelVersion`  ;;

            packaging) versionLookup[packaging]=`echo $wheelVersion` ;;
            more_itertools)  versionLookup[more_itertools]=`echo $wheelVersion` ;;
            importlib_metadata)  versionLookup[importlib_metadata]=`echo $wheelVersion`  ;;
            immutables)  versionLookup[immutables]=`echo $wheelVersion`  ;;
            attrs)  versionLookup[attrs]=`echo $wheelVersion`  ;;
    esac

done


for FILE in ./fdk_dependencies/*.tar.gz
do
    fileName=`echo $FILE`
    fileName=${fileName:19}

    case $fileName in
        contextvars-*)  versionLookup[contextvars]=`echo $fileName| grep -o -P '(?<=contextvars-).*(?=.tar.gz)'`  ;;
        pytest-asyncio-*)  versionLookup[pytest-asyncio]=`echo $fileName| grep -o -P '(?<=pytest-asyncio-).*(?=.tar.gz)'`  ;;
    esac

done

rpmbuild --define "_rpm_version ${RPM_VERSION}" --define "_pytest_version ${versionLookup[pytest]}"  --define "_pbr_version ${versionLookup[pbr]}"  --define "_iso_version ${versionLookup[iso8601]}"  --define "_pytest_asyncio_version ${versionLookup[pytest-asyncio]}"  --define "_contextvars_version ${versionLookup[contextvars]}"  --define "_httptools_version ${versionLookup[httptools]}"  --define "_zipp_version ${versionLookup[zipp]}"  --define "_wcwidth_version ${versionLookup[wcwidth]}"  --define "_typing_extensions_version ${versionLookup[typing_extensions]}"  --define "_pyparsing_version ${versionLookup[pyparsing]}"  --define "_py_version ${versionLookup[py]}"  --define "_pluggy_version ${versionLookup[pluggy]}"  --define "_packaging_version ${versionLookup[packaging]}"  --define "_more_itertools_version ${versionLookup[more_itertools]}"  --define "_importlib_metadata_version ${versionLookup[importlib_metadata]}"  --define "_immutables_version ${versionLookup[immutables]}"   --define "_attrs_version ${versionLookup[attrs]}" -ba fdk-python36.spec 



mkdir -p  /temp_rpm/rpm-package
cp -r ~/rpmbuild/RPMS/x86_64/*  /temp_rpm/rpm-package
cp -r ~/rpmbuild/SRPMS/*  /temp_rpm/rpm-package