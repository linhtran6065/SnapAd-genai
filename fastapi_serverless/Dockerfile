FROM python:3.10.11-slim-buster

RUN apt-get update && apt-get upgrade -y


COPY builder/requirements.txt /requirements.txt
RUN python3.10 -m pip install -r /requirements.txt && \
    rm /requirements.txt


# NOTE: The base image comes with multiple Python versions pre-installed.
#       It is reccommended to specify the version of Python when running your code.

# Add src files (Worker Template)
ADD src .

# EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000