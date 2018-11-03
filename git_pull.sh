#!/bin/bash

git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=9999999'
git pull


