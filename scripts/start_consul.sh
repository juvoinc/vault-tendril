#!/bin/bash

consul agent -dev -advertise 127.0.0.1> /dev/null 2>&1 &
