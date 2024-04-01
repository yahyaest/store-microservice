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

store_ip=$(getent hosts store | awk '{ print $1 }')
# echo "$store_ip game.store.app" >> /etc/hosts
notification_ip=$(getent hosts notification | awk '{ print $1 }')
gateway_ip=$(getent hosts gateway | awk '{ print $1 }')

if [ "$ENV" = "PROD" ]
then
        export WS_BASE_URL=ws://$store_ip:5001
else
        export WS_BASE_URL=ws://$store_ip:5000
fi
export NOTIFICATION_BASE_URL=http://$notification_ip:8000
export GATEWAY_BASE_URL=http://$gateway_ip:3000
export JWT_SECRET='super-secret'

yes | python manage.py makemigrations > /dev/stderr
yes | python manage.py makemigrations api > /dev/stderr
yes yes | python manage.py migrate > /dev/stderr


if [ "$ENV" = "PROD" ]
then
        daphne -b 0.0.0.0 -p 5001 store_app.asgi:application > /dev/stderr &

        yes yes | uwsgi  --protocol $PROTOCOL --master \
        --socket $SOCKET --chdir $CHDIR --wsgi-file $WSGIFILE --callable $CALLABLE  --processes $PROCESSES \
        --threads $THREADS --buffer-size $BUFFERSIZE --stats  $STATS  > /dev/stderr

else
        python manage.py runserver 0.0.0.0:5000 > /dev/stderr
fi
