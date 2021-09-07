#!/bin/bash

#./manage.py migrate --sdir ./results_test --tdir ./tsr_t --no_rename --ratio 0.7
#./manage.py migrate --sdir ./results_test --tdir ./tsr_t --ratio 0.7
#./manage.py migrate --sdir ./results_test --tdir ./tsr_t --ratio 0.7 --label_include 1
#./manage.py migrate --sdir ./results_test --tdir ./tsr_t --ratio 0.7 --label_include 'Stop sign - Oct'
./manage.py migrate --sdir ./results_test --tdir ./tsr_t --ratio 0.7 --label_exclude 'Stop sign - Oct'
