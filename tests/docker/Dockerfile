ARG base_image

FROM ${base_image}
WORKDIR /ao-env

ENV TEST_USER=testuser SUDO_GROUP=sudo
RUN set -xe && \
  apt-get -q update && \
  apt-get -y -q install sudo && \
  groupadd -r ${TEST_USER} && \
  useradd -m -g ${TEST_USER} ${TEST_USER} && \
  usermod -aG ${SUDO_GROUP} ${TEST_USER} && \
  mkdir -p /etc/sudoers.d && \
  echo "${TEST_USER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${TEST_USER} && \
  chmod 0440 /etc/sudoers.d/${TEST_USER}

COPY . /home/testuser/.local/share/ao-env

RUN chown -R testuser:testuser /home/testuser/.local

USER $TEST_USER
#RUN /bin/bash
