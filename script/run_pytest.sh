BASEDIR=$(dirname "$0")

cd $BASEDIR/../test/pytest
python -m unittest decoder_test.py
