#!/usr/bin/env bash

cd $(dirname $(readlink -f $0))

sudo aptitude update -q=2
sudo aptitude install -q=1 libxml2-dev libxslt1-dev zlib1g-dev python3 python3-pip python3-apsw python3-bottle python3-mockito

sudo pip3 install feedgen --upgrade

mkdir -p deps
cd deps

(
    if [ -d feedparser ]; then
        cd feedparser
        git reset --hard
        git pull origin master
    else
        git clone https://github.com/kurtmckee/feedparser.git
        cd feedparser
    fi
    sudo python3 setup.py install
)
