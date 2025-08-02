FROM python:3.11.2-slim

COPY ./src/ /app/
WORKDIR /app

# OS level installs
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    libpq-dev \
    gcc \
    make

# venv install
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/pip install -r /app/requirements.txt

# purge unused packages
RUN apt-get remove -y --purge make gcc build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# set PATH to use venv by default
ENV PATH="/opt/venv/bin:$PATH"



# make entrypoint executable
RUN chmod +x ./config/entrypoint.sh

CMD ["./config/entrypoint.sh"]
