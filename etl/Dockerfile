FROM public.ecr.aws/lambda/python:3.11

COPY run_pipeline.py ${LAMBDA_TASK_ROOT}/
COPY requirements.txt  ${LAMBDA_TASK_ROOT}/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["run_pipeline.lambda_handler"]