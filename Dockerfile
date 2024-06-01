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
    apk add --no-cache python3 py3-pip && \
    python3 -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip3 install --no-cache-dir -r /app/bloodytools/requirements-dev.txt

# Enable python venv in entrypoint
ENV PATH="/app/.venv/bin:$PATH"

## set bloodytools entrypoint, this container will be usable like a command line tool
COPY . /app/bloodytools
WORKDIR /app/bloodytools
ENTRYPOINT ["python3", "-m", "bloodytools"]
CMD ["--help"]
