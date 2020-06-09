FROM avdteam/base
LABEL maintainer="TiTom73<tom@inetsix.net>"

# Default ARG values

# Set term option
ARG TERM=xterm

# Install necessary packages
# Install systemd -- See https://hub.docker.com/_/centos/
RUN yum -y update; yum -y install \
    findutils \
    make \
    which \
    python3 \
    python3-pip \
    rpm-build \
    wget \
    xorg-x11-server-Xvfb \
    xorg-x11-fonts-Type1 \
    xorg-x11-fonts-75dpi \
    && yum clean all

RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-rc/wkhtmltox-0.12.6-0.20200605.30.rc.faa06fa.centos8.x86_64.rpm && \
    yum localinstall -y *.rpm

# Create the /project directory and add it as a mountpoint
WORKDIR /projects
VOLUME ["/projects"]

COPY . /projects/

# Install python modules required by the repo
RUN pip3 install -r requirements.txt

# Use Airsta_Chack as entrypoint
CMD ["python3", "run.py"]