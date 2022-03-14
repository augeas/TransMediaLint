#!/bin/bash
until $(curl --output /dev/null --silent --head --fail http://localhost:6800); do
    printf 'waiting for scrapyd...'
    sleep 5
done

cd /transmedialint/scrapers

for dir in $(find . -maxdepth 1 -mindepth 1 -type d); do
	cd $dir
    if [ -e scrapy.cfg ]; then
        scrapyd-deploy --build-egg=scrape.egg
        rm scrape.egg
        python3 setup.py sdist && python3 setup.py install
        scrapyd-deploy --egg=./dist/project-1.0-py3.9.egg
    fi
    cd ..
done
