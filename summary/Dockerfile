FROM python:3.13-slim-bullseye

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN apt-get update && \
    apt-get install -y curl gnupg gcc g++ unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean

COPY create_summaries.py .

CMD python3 create_summaries.py