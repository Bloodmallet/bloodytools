# base image
FROM ubuntu:latest AS builder

# install SimulationCraft
RUN apt-get update && apt-get install -y \
    build-essential \
    git && \
    git clone --depth 1 https://github.com/simulationcraft/simc.git /app/SimulationCraft && \
    make -C /app/SimulationCraft/engine optimized -j 2 SC_NO_NETWORKING=1

FROM  ubuntu:latest AS worker
# get built file
COPY --from=builder /app/SimulationCraft/engine/simc /app/SimulationCraft/engine/
COPY --from=builder /app/SimulationCraft/profiles/ /app/SimulationCraft/profiles/

# install bloodytools
COPY ./requirements.txt /app/bloodytools/
WORKDIR /app
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip && \
    python3 -m pip install --upgrade pip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r bloodytools/requirements.txt

# remove obsolete simc files
# RUN find /app/SimulationCraft -maxdepth 1 -type f
# RUN rm $(find /app/SimulationCraft -maxdepth 1 -type f)

## get bloodytools
COPY . /app/bloodytools
WORKDIR /app/bloodytools/bloodytools
ENTRYPOINT ["python3", "./bloodytools.py", "--executable", "../../SimulationCraft/engine/simc"]
CMD ["--help"]
