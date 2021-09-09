#!/bin/bash

#./manage.py migrate --sdir ./results --tdir ./tsr --ratio 1.0
./manage.py migrate --sdir ./tsr --tdir ./tsr_ex --ratio 0.9 --label_include 'Stop sign - Oct' --no_rename
