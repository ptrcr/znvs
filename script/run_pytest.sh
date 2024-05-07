BASEDIR=$(dirname "$0")
REPORT="${1:-test_report.xml}"
cd $BASEDIR/../test/pytest
pytest --junit-xml $REPORT
