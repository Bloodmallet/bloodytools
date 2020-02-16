# base image
FROM alpine:latest

# install requirements
RUN apk --no-cache add --virtual build_dependencies \
    git \
    g++ \
    make && \
    apk --no-cache add python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    python3 -m ensurepip && \
    python3 -m pip install --upgrade pip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi


# prepare SimulationCraft
RUN git clone --depth 1 https://github.com/simulationcraft/simc.git /app/SimulationCraft
WORKDIR /app/SimulationCraft/engine
# -j is the number of threads used for compiling...ideally that should be a system variable
RUN make optimized -j 2 SC_NO_NETWORKING=1

# TODO: remove simc files here

# handle bloodytools requirements
COPY ./requirements.txt /app/bloodytools/
WORKDIR /app
# installing into base...it's a container, deal with it
RUN pip3 install --no-cache-dir -r bloodytools/requirements.txt

# remove obsolete build_dependencies
RUN apk del build_dependencies

# copy project into container
COPY . /app/bloodytools

# enable direct container usage
WORKDIR /app/bloodytools/bloodytools
ENTRYPOINT ["python3", "./bloodytools.py", "--executable", "../../SimulationCraft/engine/simc"]
CMD ["--help"]
