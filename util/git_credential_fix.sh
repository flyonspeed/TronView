#!/bin/bash

git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=9999999'

read -s -p "Enter github user name: " githubuser ; printf "\n"

echo url=https://$githubuser@github.com | git credential reject

