# FROM public.ecr.aws/lambda/python:3.13

# WORKDIR ${LAMBDA_TASK_ROOT}/

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY extract.py .
# COPY transform.py .
# COPY load.py .
# COPY run_pipeline.py .

# RUN yum install gcc-c++ python3-devel unixODBC-devel
# RUN ln -s $(ls /usr/libexec/gcc/x86_64-amazon-linux/ | sort -V | tail -n 1)/cc1plus /usr/bin/
# RUN pip install --user pyodbc

# CMD ["run_pipeline.lambda_handler"]

# --- Base image: AWS Lambda Python runtime ---
FROM public.ecr.aws/lambda/python:3.13
# --- Install system dependencies for pyodbc ---
WORKDIR ${LAMBDA_TASK_ROOT}

# RUN dnf -y update && \
#     dnf -y install \
#         unixODBC \
#         unixODBC-devel \
#         curl \
#         gnupg2 && \
#     curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/pki/rpm-gpg/Microsoft.asc && \
#     curl https://packages.microsoft.com/config/rhel/8/prod.repo | tee /etc/yum.repos.d/mssql-release.repo && \
#     ACCEPT_EULA=Y dnf -y install msodbcsql18 mssql-tools18 && \

RUN dnf update -y && \
    dnf install -y unixODBC-devel gcc gcc-c++ && \
    curl https://packages.microsoft.com/config/rhel/8/prod.repo > /etc/yum.repos.d/mssql-release.repo && \
    ACCEPT_EULA=Y dnf install -y msodbcsql18 && \
    dnf clean all

# --- Copy requirements and install Python dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# --- Copy application code ---
COPY extract.py .
COPY transform.py .
COPY load.py .
COPY run_pipeline.py .
# --- Command to run your Lambda handler ---
CMD [ "run_pipeline.lambda_handler" ]