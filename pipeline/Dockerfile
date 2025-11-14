FROM python:3.13-slim-bullseye

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# These commands install msodbcsql18 to make the loading script work
RUN apt-get update && \
    apt-get install -y curl gnupg gcc g++ unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean

COPY extract.py transform.py load.py ./

CMD python3 extract.py && python3 transform.py && python3 load.py