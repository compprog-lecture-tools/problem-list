FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --no-install-suggests \
      make g++ python3 python3-pip git texlive texlive-latex-extra texlive-science texlive-fonts-extra \
      latexmk rsync openssh-client gdebi-core xz-utils curl && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_20.04/amd64/libipe_7.2.20-1_amd64.deb -o /libipe.deb && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_20.04/amd64/ipe_7.2.20-1_amd64.deb -o /ipe.deb && \
    gdebi -n /libipe.deb && \
    gdebi -n /ipe.deb && \
    apt-get purge -y gdebi-core xz-utils curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /libipe.deb /ipe.deb && \
    pip3 install pygments
