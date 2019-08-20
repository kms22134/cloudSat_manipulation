#!/bin/bash

python3 setup.py bdist_wheel
pip3 uninstall dist/cloudsat_object_manipulation-0.1.0-cp37-cp37m-linux_x86_64.whl
pip3 install dist/cloudsat_object_manipulation-0.1.0-cp37-cp37m-linux_x86_64.whl
