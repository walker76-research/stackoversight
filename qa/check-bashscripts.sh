#!/bin/bash

# Script to check all BASH scripts by ShellCheck validator

pass=0
fail=0

function check_files() {
    for source in $1
    do
        echo "$source"
        shellcheck -e 2181 -e 1091 "$source"
        if [ $? -eq 0 ]
        then
            echo "    Pass"
            let "pass++"
        elif [ $? -eq 2 ]
        then
            echo "    Illegal usage (should not happen)"
            exit 2
        else
            echo "    Fail"
            let "fail++"
        fi
    done
}

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

pushd "${SCRIPT_DIR}/.."
files=$(find . -path "./venv" -prune -o -path "./ee_tests/node_modules" -prune -o -path "./ee_tests/target" -prune -o -name '*.sh' -print)
check_files "$files"
popd

if [ $fail -eq 0 ]
then
    echo "All checks passed for $pass source files"
else
    let total=$pass+$fail
    echo "BASH-related issues should be fixed in $fail source files out of $total files"
    exit 1
fi
