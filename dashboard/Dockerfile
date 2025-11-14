FROM python:3.13-slim-bullseye

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# This run command installs msodbcsql18, unixodbc and their required dependencies so that the pyodbc python library will function correctly.
# This involves making sure gcc is installed and up to date, as well as verifying with a microsoft key and accepting the EULA
RUN apt-get update && \
    apt-get install -y curl gnupg gcc g++ unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean

COPY streamlit_dashboard.py .
COPY extract_dashboard.py .

# Streamlit port
EXPOSE 8501

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENTRYPOINT ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]