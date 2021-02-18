#!/bin/bash
requirements_folder="tests/versions_requirement"

function run_test() {
    echo "================================================================================" >> test_report.txt
    python3 -m venv venv
    source venv/bin/activate
    pip install pytest
    pip install -r "$requirements_folder/$1"
    pytest -s >> test_report.txt
    deactivate
    rm -rf venv
    echo "" >> test_report.txt
    echo "" >> test_report.txt
}

touch test_report.txt
echo "" > test_report.txt

for requirement in `ls $requirements_folder`
do 
    run_test $requirement
done