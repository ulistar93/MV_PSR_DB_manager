#!/bin/bash

./manage.py migrate --sdir ./results --tdir ./tsr
./manage.py extract --sdir ./tsr --tdir ./tsr_ex --include "Stop sign - Oct"
