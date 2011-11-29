function test {
    echo
    echo "===================== $1 ====================="
    source ~/virtualenvs/behave$1/bin/activate
    cd ~/src/projects/behave
    rm -rf build
    $2 setup.py build
    $2 tools/create_test_features.py
    cd build/lib/
    echo "--------------------- $1 UNIT TESTS --------------------------"
    ~/virtualenvs/behave$1/bin/nosetests
    echo "--------------------- $1 FRENCH FEATURE --------------------------"
    python -m behave.__main__ features-fr --i18n=fr
    cd ../../
    echo "--------------------- $1 DONE --------------------------"
    echo
}

test py2.5 python
test py2.6 python
test py2.7 python
test py3.2 python
test pypy pypy
test jy2.5 jython

