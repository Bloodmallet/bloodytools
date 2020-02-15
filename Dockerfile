# base image
FROM ubuntu:latest

# install requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    pkg-config \
    python3 \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*
# if SimulationCraft build happens with SC_NO_NETWORKING=1 libcurl-dev is not required
#     libcurl-dev \
# update pip
RUN python3 -m pip install --upgrade pip

# prepare SimulationCraft
RUN git clone --depth 1 https://github.com/simulationcraft/simc.git /app/SimulationCraft
WORKDIR /app/SimulationCraft/engine
# -j is the number of threads used for compiling...ideally that should be a system variable
RUN make optimized -j 2 SC_NO_NETWORKING=1

# handle bloodytools requirements
COPY ./requirements.txt /app/bloodytools/
WORKDIR /app
# installing into base...it's a container, deal with it
RUN pip3 install --no-cache-dir -r bloodytools/requirements.txt

# copy project into container
COPY . /app/bloodytools

# enable direct container usage
WORKDIR /app/bloodytools/bloodytools
ENTRYPOINT ["python3", "./bloodytools.py", "--executable", "../../SimulationCraft/engine/simc"]
CMD ["--help"]
