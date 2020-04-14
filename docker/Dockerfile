FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests \
    make g++-8 python3 python3-pip git texlive texlive-latex-extra latexmk gdebi-core xz-utils curl && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_18.04/amd64/libipe_7.2.13-1_amd64.deb -o /libipe.deb && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_18.04/amd64/ipe_7.2.13-1_amd64.deb -o /ipe.deb && \
    gdebi -n /libipe.deb && \
    gdebi -n /ipe.deb && \
    apt-get purge -y gdebi-core xz-utils curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /libipe.deb /ipe.deb
