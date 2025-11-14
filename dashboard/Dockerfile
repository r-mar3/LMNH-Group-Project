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

# Streamlit port
EXPOSE 8501

CMD streamlit run streamlit_dashboard.py