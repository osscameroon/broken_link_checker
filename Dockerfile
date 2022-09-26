FROM python:3-alpine

WORKDIR /blc

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY blc/* ./blc/

ENTRYPOINT ["python", "-m", "blc"]
