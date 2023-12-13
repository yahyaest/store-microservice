FROM python:3.11-alpine3.17

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt


RUN apk --no-cache update && apk add curl postgresql-dev uwsgi uwsgi-python3 gcc python3-dev musl-dev libffi-dev build-base alpine-sdk \
    && pip install --upgrade pip \
    && pip install --prefix=/install --no-warn-script-location -r /requirements.txt \
    && find /install \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /install \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps


FROM python:3.11-alpine3.17
COPY --from=0 /install /usr/local
RUN apk --no-cache add libpq libstdc++ gcc libgcc linux-headers uwsgi uwsgi-python3

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip


# ENV PYTHONPATH=/code
ENV PYTHONUNBUFFERED=0

# COPY entrypoint.sh /entrypoint.sh
# RUN chmod 777 /code/entrypoint.sh

CMD ["sh", "-c", "tail -f /dev/null"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]


 
