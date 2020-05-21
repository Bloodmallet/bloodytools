# base image
FROM alpine:latest AS build

ARG THREADS=1

# install SimulationCraft
RUN apk --no-cache add --virtual build_dependencies \
    git \
    g++ \
    make && \
    git clone --depth 1 https://github.com/simulationcraft/simc.git /app/SimulationCraft && \
    make -C /app/SimulationCraft/engine optimized -j $THREADS SC_NO_NETWORKING=1 LTO_THIN=1 OPTS+="-Os -mtune=native" && \
    apk del build_dependencies

# disable ptr to reduce build size
# sed -i '' -e 's/#define SC_USE_PTR 1/#define SC_USE_PTR 0/g' engine/dbc.hpp

# fresh container
FROM alpine:latest

# get compiled simc and profiles
COPY --from=build /app/SimulationCraft/engine/simc /app/SimulationCraft/engine/
COPY --from=build /app/SimulationCraft/profiles/ /app/SimulationCraft/profiles/

# install bloodytools
COPY ./requirements.txt /app/bloodytools/
WORKDIR /app
RUN apk --no-cache add --virtual build_dependencies \
    git \
    libgcc \
    libstdc++ && \
    apk --no-cache add python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    python3 -m ensurepip && \
    python3 -m pip install --upgrade pip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    pip3 install --no-cache-dir -r bloodytools/requirements.txt

## set bloodytools entrypoint, this container will be usable like a command line tool
COPY . /app/bloodytools
WORKDIR /app/bloodytools
ENTRYPOINT ["python3", "-m", "bloodytools", "--executable", "../SimulationCraft/engine/simc"]
CMD ["--help"]
