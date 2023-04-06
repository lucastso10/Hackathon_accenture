FROM nvidia/cuda:11.3.0-base-ubuntu20.04
ARG TOKEN
ENV PYTHONBUFFERED 1

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-venv python3-pip libgl1-mesa-glx libglib2.0-0
RUN pip install -U pip

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt --extra-index-url https://$TOKEN@pkgs.dev.azure.com/LiquidStudiosBrazil/139e3811-b61c-447b-9ab0-4c6d8a4d9008/_packaging/aiv/pypi/simple

ENTRYPOINT ["tail", "-f", "/dev/null"]
