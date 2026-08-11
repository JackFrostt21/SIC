FROM python:3.10.4-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/var/app

# copy project
COPY . $APP_HOME/
COPY ./manage.py $APP_HOME/manage.py
COPY ./entrypoint.prod.sh $APP_HOME/entrypoint.sh
COPY ./requirements.txt $APP_HOME/requirements.txt
COPY ./static $APP_HOME/static

WORKDIR $APP_HOME

RUN apt update
RUN pip install --upgrade pip
RUN pip install -r $APP_HOME/requirements.txt

EXPOSE 8000

RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
