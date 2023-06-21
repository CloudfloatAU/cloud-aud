FROM python:3.9-slim as builder


# Install Linux dependencies.
RUN apt-get update \
    && apt-get install -y gcc openssh-client git \
    && apt-get clean

# Copy files and set working directory.
COPY . /app
WORKDIR /app

# Install Python dependencies.
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt && \
    pip install --user -r docs/requirements.txt

# Set up ape.
RUN /root/.local/bin/ape plugins install . && \
    ape compile --size

# Run the container.
ENTRYPOINT bash
