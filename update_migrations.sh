#!/bin/bash
container=$(docker ps | grep -o transmedialint_transmedialint_[0-9a-f])
docker exec $container python manage.py makemigrations
#docker exec $container python manage.py migrate
for pyfile in `docker exec $container ./list_migrations.sh` ;
do docker cp $container:/transmedialint/$pyfile transmedialint/$pyfile ;
done
