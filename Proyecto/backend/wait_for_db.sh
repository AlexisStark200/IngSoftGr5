#!/bin/bash
# wait_for_db.sh

set -e

host="db"
port="3306"
cmd="$@"

until mysql -h "$host" -P "$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e 'SELECT 1'; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "MySQL is up - executing command"
exec $cmd