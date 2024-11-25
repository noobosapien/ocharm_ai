#!/bin/sh

export PGUSER="postgres"

psql -c "CREATE DATABASE user"

psql inventory -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"