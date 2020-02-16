# base image
FROM alpine:latest

# install SimulationCraft
RUN apk --no-cache add --virtual build_dependencies \
    git \
    g++ \
    make && \
    git clone --depth 1 https://github.com/simulationcraft/simc.git /app/SimulationCraft && \
    make -C /app/SimulationCraft/engine optimized -j 2 SC_NO_NETWORKING=1 && \
    apk del build_dependencies

# install bloodytools
COPY ./requirements.txt /app/bloodytools/
WORKDIR /app
RUN apk --no-cache add --virtual build_dependencies \
    git && \
    apk --no-cache add python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    python3 -m ensurepip && \
    python3 -m pip install --upgrade pip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    pip3 install --no-cache-dir -r bloodytools/requirements.txt && \
    apk del build_dependencies

# remove obsolete simc files
# RUN find /app/SimulationCraft -maxdepth 1 -type f
# RUN rm $(find /app/SimulationCraft -maxdepth 1 -type f)

## get bloodytools
COPY . /app/bloodytools
WORKDIR /app/bloodytools/bloodytools
ENTRYPOINT ["python3", "./bloodytools.py", "--executable", "../../SimulationCraft/engine/simc"]
CMD ["--help"]
