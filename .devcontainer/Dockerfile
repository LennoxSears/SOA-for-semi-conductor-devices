FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install Python and required packages for Excel analysis
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && pip3 install --no-cache-dir \
    pandas \
    openpyxl \
    xlrd \
    numpy \
    matplotlib \
    seaborn \
    jupyter \
    pyyaml \
    jsonschema
