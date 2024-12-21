#!/bin/bash

while true
do
    # try pypy3 first if it exists
    if command -v pypy3 &> /dev/null
    then
        pypy3 main.py
    else
        python3 main.py
    fi
    sleep 1800
    if [ $? -eq 130 ]
    then
        break
    fi
done
