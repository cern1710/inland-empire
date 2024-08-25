#!/bin/bash

PID=$(ps aux | grep -v grep | grep mongod | awk '{print $2}')

if [ -z "$PID" ]; then
  echo "mongod process not found."
else
  kill $PID
  echo "mongod process (PID: $PID) has been terminated."
fi