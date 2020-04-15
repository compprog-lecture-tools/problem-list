FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests \
      make g++-8 python3.7 python3-pip git texlive texlive-latex-extra texlive-science \
      latexmk rsync openssh-client gdebi-core xz-utils curl && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_18.04/amd64/libipe_7.2.13-1_amd64.deb -o /libipe.deb && \
    curl -L https://download.opensuse.org/repositories/home:/otfried13/xUbuntu_18.04/amd64/ipe_7.2.13-1_amd64.deb -o /ipe.deb && \
    gdebi -n /libipe.deb && \
    gdebi -n /ipe.deb && \
    apt-get purge -y gdebi-core xz-utils curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /libipe.deb /ipe.deb && \
    # After this command, the python3-pip (a.k.a. pip using the default python 3.6) now uses python3.7
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 1 && \
    pip3 install pygments
