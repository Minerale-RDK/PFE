#!/bin/bash

if [ ! -d "certificates-all/" ]; then
	mkdir certificates-all
else
	echo "certificates directory exists"
fi

if [ ! -d "data/" ]; then
	mkdir data
else
	echo "data directory exists"
fi


python3 BuildDockerCompose.py