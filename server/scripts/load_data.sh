#!/bin/sh

echo "\e[0;32mStart data loading...\e[0m"
python3 load_data.py
if [ $? -ne 0 ]
then
    echo "\e[1;31mData loading failed\e[0m"
    exit 1
fi
echo "\e[1;32mData loaded successfully\e[0m"
