FROM debian:buster-slim as build

ENV LANG C.UTF-8

# IFDEF PROXY
#! RUN echo 'Acquire::http { Proxy "http://${APT_PROXY_HOST}:${APT_PROXY_PORT}"; };' >> /etc/apt/apt.conf.d/01proxy
# ENDIF

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        python3 python3-dev python3-pip python3-venv python3-setuptools \
        espeak libsndfile1 git \
        llvm-7-dev libatlas-base-dev libopenblas-dev gfortran \
        ca-certificates

RUN apt-get install python3-pip

ENV LLVM_CONFIG=/usr/bin/llvm-config-7

COPY source/ /source/

RUN mkdir -p /app && \
    cd /app && \
    if [ -f '/source/TTS.tar.gz' ]; then \
      tar -C /app -xf /source/TTS.tar.gz; \
    else \
      git clone https://github.com/mozilla/TTS; \
    fi

#ENV VENV=/app/venv
#RUN python3 -m venv ${VENV}

# IFDEF PROXY
#! ENV PIP_INDEX_URL=http://${PYPI_PROXY_HOST}:${PYPI_PROXY_PORT}/simple/
#! ENV PIP_TRUSTED_HOST=${PYPI_PROXY_HOST}
# ENDIF

# Set up Python virtual environment
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org  --upgrade 'pip==20.3.1' && \
    pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org  --upgrade wheel setuptools

# Target architecture
ARG TARGETARCH
ARG TARGETVARIANT

# Copy shared and architecture-specific files
COPY download/shared/ /download/
COPY download/${TARGETARCH}${TARGETVARIANT}/ /download/

# IFDEF NOAVX
#! RUN mv download/noavx/* download/
# ENDIF

# Install torch from local cache if present
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -f /download --no-index --no-deps 'torch==1.6.0' || true

# Install the rest of the requirements
RUN cd /app/TTS && \
    if [ -f /download/requirements.txt ]; then cp /download/requirements.txt . ; fi && \
    pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install -f /download -r requirements.txt

# Install MozillaTTS itself
RUN cd /app/TTS && \
    python3 setup.py install

# Packages needed for web server
#RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org  -f download/ 'flask' 'flask-cors'

# -----------------------------------------------------------------------------

#FROM debian:buster-slim

#ENV LANG C.UTF-8

# IFDEF PROXY
#! RUN echo 'Acquire::http { Proxy "http://${APT_PROXY_HOST}:${APT_PROXY_PORT}"; };' >> /etc/apt/apt.conf.d/01proxy
# ENDIF

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        python3 python3-distutils python3-llvmlite libpython3.7 \
        espeak libsndfile1 git \
        espeak \
        libsndfile1 libgomp1 libatlas3-base libgfortran4 libopenblas-base \
        libjbig0 liblcms2-2 libopenjp2-7 libtiff5 libwebp6 libwebpdemux2 libwebpmux3 \
        libnuma1
		


# IFDEF PROXY
#! RUN rm -f /etc/apt/apt.conf.d/01proxy
# ENDIF

#COPY --from=build /app/venv/ /app/

ARG LANGUAGE=en
COPY models/ /app/model/
COPY tts_api/ /app/tts_api/
#COPY run.sh /

WORKDIR /app

EXPOSE 8081

#ENTRYPOINT ["/bin/bash", "/run.sh"]