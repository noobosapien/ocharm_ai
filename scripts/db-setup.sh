#!/bin/sh

export PGUSER="postgres"

psql -c "CREATE DATABASE user"

psql postgres -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"