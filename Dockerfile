FROM python:3.11-slim-bookworm
RUN pip install requests pytest pytest-dependency pytest-retry
WORKDIR /tmp
ENTRYPOINT [ "pytest" ]
