python -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -r requirements.txt
pip install dist/blc-*-py3-none-any.whl
tests/checker_test.sh