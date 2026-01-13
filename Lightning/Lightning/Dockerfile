FROM python:3.10.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/var/app

# copy project
COPY . $APP_HOME/
# COPY ./manage.py $APP_HOME/manage.py
# COPY ./entrypoint.prod.sh $APP_HOME/entrypoint.sh
# COPY ./requirements.txt $APP_HOME/requirements.txt


# chown all the files to the app user
WORKDIR $APP_HOME

# Устанавливаем зависимости
RUN apt update
RUN pip install --upgrade pip
RUN pip install -r $APP_HOME/requirements.txt

EXPOSE 8080

RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
