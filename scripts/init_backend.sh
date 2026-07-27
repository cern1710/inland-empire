#!/bin/bash

DB_PATH=~/data/db
LOG_PATH=~/data/log/mongodb/mongo.log

mongod --dbpath "$DB_PATH" --logpath "$LOG_PATH" --fork

redis-server