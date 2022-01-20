#!/bin/bash
docker-compose stop
sleep 5
docker-compose rm -a -f
docker volume rm pfe_volume1
