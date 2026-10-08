FROM python:3.11

WORKDIR /blc

COPY . /blc/

RUN pip install uv

RUN uv lock
RUN uv sync

ENTRYPOINT ["uv", "run", "python", "-m", "blc"]
