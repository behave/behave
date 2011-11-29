#!/bin/sh

if [ x"$BEHAVE_DIR" != x"" ]; then
    behave_dir=$BEHAVE_DIR
	venv_dir=$behave_dir/tools/virtualenvs
else
    case "`dirname $0`" in
    tools)
        behave_dir="."
        venv_dir="tools/virtualenvs"
        ;;
    .)
        behave_dir=".."
        venv_dir="virtualenvs"
        ;;
    "")
        behave_dir=".."
        venv_dir="virtualenvs"
        ;;
    *)
        echo "Must be run from behave directory or provide BEHAVE_DIR env var"
        exit 1
        ;;
    esac
fi

behave_dir=`cd $behave_dir; pwd`
venv_dir=`cd $venv_dir; pwd`

function check_venv {
    if [ ! -d $venv_dir ]; then
        mkdir -p $venv_dir
        mkdir -p $venv_dir/cache
    fi

    case $1 in
    pypy*)
        python=`which pypy`
        ;;
    py*)
        python=`echo $1 | sed -e s/py/python/`
        python=`which $python`
        ;;
    jy2.5)
        python=`which jython`
        ;;
    esac

    if [ ! -d $venv_dir/behave$1 ]; then
        echo "===================== $1 CREATING VIRTUALENV ====================="
        $python `which virtualenv` --no-site-packages --distribute --python=$python $venv_dir/behave$1
    fi

    echo "===================== $1 CHECKING PACKAGES ====================="

    $venv_dir/behave$1/bin/pip install --download-cache=$venv_dir/cache nose mock parse argparse
}

failed=""

function test_version {
    case $1 in
    pypy)
        python=pypy
        ;;
    py*)
        python=python
        ;;
    jy*)
        python=jython
        ;;
    esac

    echo
    echo "===================== $1 ====================="
    source $venv_dir/behave$1/bin/activate
    cd $behave_dir
    rm -rf build
    $python setup.py build
    $python tools/create_test_features.py
    cd build/lib/
    echo "--------------------- $1 UNIT TESTS --------------------------"
    $venv_dir/behave$1/bin/nosetests || failed="$failed $1"
    echo "--------------------- $1 FRENCH FEATURE --------------------------"
    $python -m behave.__main__ features-fr --i18n=fr
    cd ../../
    echo "--------------------- $1 DONE --------------------------"
    echo
}

if [ x"$*" != x"" ]; then
    versions="$*"
else
    versions="py2.5 py2.6 py2.7 py3.2 pypy1.7 jy2.5"
fi

for version in $versions; do
    check_venv $version
    test_version $version
done

if [ x"$failed" != x"" ]; then
    echo "Versions failed:$failed"
fi
