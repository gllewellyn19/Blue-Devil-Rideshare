#!/bin/bash
psql -h db -U rideshare -d production -a -f create.sql
psql -h db -U rideshare -d production -a -f load.sql
