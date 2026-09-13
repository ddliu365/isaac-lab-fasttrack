# Isaac Lab Fast-Track image.
# Starts from NVIDIA's prebuilt Isaac Lab container (headless-only, already has Isaac Sim 5.1.0 + Isaac Lab 2.3.2 installed),
# then adds our tools and sane defaults. Build ~2 min on top of a ~20 GB pull.
ARG ISAACLAB_VERSION=2.3.2
FROM nvcr.io/nvidia/isaac-lab:${ISAACLAB_VERSION}

ENV ACCEPT_EULA=Y \
    PRIVACY_CONSENT=Y \
    OMNI_KIT_ACCEPT_EULA=YES \
    ISAACLAB_PATH=/workspace/isaaclab \
    PYTHONUNBUFFERED=1

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      git vim htop tmux less && \
    rm -rf /var/lib/apt/lists/*

COPY tools/ /opt/fasttrack/tools/
COPY scripts/container/ /opt/fasttrack/bin/
RUN chmod +x /opt/fasttrack/bin/*
ENV PATH="/opt/fasttrack/bin:${PATH}"

WORKDIR /workspace/isaaclab
CMD ["bash"]
