#! /bin/bash
set -e

ORIG_DIR=$(pwd)
TEMP_DIR=$(mktemp -d -t bolt-build-XXXXXXXXXXX)

cp -R ./bolt $TEMP_DIR
cp -R entrypoint.py $TEMP_DIR
cp -R LICENSE.txt $TEMP_DIR

pipenv lock -r > $TEMP_DIR/REQUIREMENTS.txt

pushd $TEMP_DIR

pex \
    -v \
    --python=$(which python3.6) \
    -r REQUIREMENTS.txt \
    -D $PWD \
    -f $PWD \
    -m entrypoint:main \
    -o bolt.pex \
    --validate-entry-point
    
if [[ $? -ne 0 ]]; then
    echo "Build failed!"
    exit 1
fi

mv bolt.pex $ORIG_DIR

popd
