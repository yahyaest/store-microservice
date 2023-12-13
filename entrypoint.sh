#!/bin/sh


PROTOCOL=${PROTOCOL:-http}
SOCKET=${SOCKET:-0.0.0.0:5000}
CHDIR=/code
WSGIFILE=/code/store_app/wsgi.py
PROCESSES=${PROCESSES:-4}
THREADS=${THREADS:-2}
BUFFERSIZE=524288
STATS=${STATS:-0.0.0.0:9191}
CALLABLE=${CALLABLE:-application}
ENV=PROD


yes | python manage.py makemigrations > /dev/stderr
yes | python manage.py makemigrations api > /dev/stderr
yes yes | python manage.py migrate > /dev/stderr


if [ "$ENV" = "PROD" ]
then
        yes yes | uwsgi  --protocol $PROTOCOL --master \
        --socket $SOCKET --chdir $CHDIR --wsgi-file $WSGIFILE --callable $CALLABLE  --processes $PROCESSES \
        --threads $THREADS --buffer-size $BUFFERSIZE --stats  $STATS  > /dev/stderr

else
        python manage.py runserver 0.0.0.0:5000 > /dev/stderr
fi
