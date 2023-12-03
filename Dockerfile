# base image

# fresh container
FROM alpine:latest

# get compiled simc and profiles
COPY --from=simulationcraftorg/simc /app/SimulationCraft/simc /app/SimulationCraft/simc
COPY --from=simulationcraftorg/simc /app/SimulationCraft/profiles/ /app/SimulationCraft/profiles/

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
ENTRYPOINT ["python3", "-m", "bloodytools"]
CMD ["--help"]
