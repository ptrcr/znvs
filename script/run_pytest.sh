BASEDIR=$(dirname "$0")

cd $BASEDIR/../test/pytest
python -m unittest decoding_test.py
