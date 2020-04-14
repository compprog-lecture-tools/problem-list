#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(dirname "$0")"

SUDO=""
if [[ "$(id -u)" -ne "0" ]]; then
    SUDO="sudo"
fi

echo -n 'Checking for requirements...'
if [[ ! -x "$(command -v docker)" ]]; then
    echo
    echo "Error: Docker is not installed." >&2
    exit 1
fi
if [[ ! -x "$(command -v systemctl)" ]]; then
    echo
    echo "Error: Systemd is not installed." >&2
    exit 1
fi
echo '  done'

read -r -p 'Base directory for installation (/opt/problem-list): ' BASE_DIR
BASE_DIR="${BASE_DIR:-/opt/problem-list}"
read -r -p 'Port for the web server: ' PORT
read -r -p 'Basic auth username: ' AUTH_USER
read -r -s -p 'Basic auth password: ' AUTH_PASSWORD
echo
read -r -p 'Deploy username: ' DEPLOY_USER
read -r -p 'Authorized public key for deploy user: ' DEPLOY_KEY

echo -n 'Creating base directory...'
${SUDO} mkdir -p "${BASE_DIR}"
echo '  done'

echo -n 'Filling base directory...'
${SUDO} touch "${BASE_DIR}/htpasswd"
${SUDO} chown root:root "${BASE_DIR}/htpasswd"
${SUDO} chmod 644 "${BASE_DIR}/htpasswd"
${SUDO} cp "${SCRIPT_DIR}/default.conf" "${BASE_DIR}"
${SUDO} mkdir "${BASE_DIR}/static"
echo '  done'

echo -n 'Installing systemd unit to /lib/systemd/system...'
sed -e "s|%BASEDIR%|${BASE_DIR}|g" \
    -e "s|%PORT%|${PORT}|g" \
    "${SCRIPT_DIR}/problem-list-nginx.service" \
| ${SUDO} tee "/lib/systemd/system/problem-list-nginx.service" > /dev/null
echo '  done'

echo -n 'Setting up deploy user...'
DEPLOY_USER_HOME="/home/${DEPLOY_USER}"
${SUDO} useradd -m -d "${DEPLOY_USER_HOME}" -s /bin/bash "${DEPLOY_USER}"
${SUDO} mkdir "${DEPLOY_USER_HOME}/.ssh"
${SUDO} chown "${DEPLOY_USER}:${DEPLOY_USER}" "${DEPLOY_USER_HOME}/.ssh"
${SUDO} chmod 700 "${DEPLOY_USER_HOME}/.ssh"
echo "${DEPLOY_KEY}" | ${SUDO} tee "${DEPLOY_USER_HOME}/.ssh/authorized_keys" > /dev/null
${SUDO} chown "${DEPLOY_USER}:${DEPLOY_USER}" "${DEPLOY_USER_HOME}/.ssh/authorized_keys"
${SUDO} chmod 644 "${DEPLOY_USER_HOME}/.ssh/authorized_keys"
${SUDO} chown "${DEPLOY_USER}:${DEPLOY_USER}" "${BASE_DIR}/static"
${SUDO} chmod 755 "${BASE_DIR}/static"
echo '  done'

echo -n 'Generating basic auth file using nginx container...'
${SUDO} docker pull nginx:1.17-alpine
echo "${AUTH_PASSWORD}" | \
    ${SUDO} docker run --rm -i \
        -v "$(realpath "${SCRIPT_DIR}/setup-password.sh"):/setup-password.sh:ro" \
        -v "$(realpath "${BASE_DIR}/htpasswd"):/htpasswd" \
        -e "USER=${AUTH_USER}" \
        nginx:1.17-alpine sh /setup-password.sh
echo '  done'

echo -n 'Reloading systemd daemon to install unit...'
${SUDO} systemctl daemon-reload
echo '  done'

cat <<EOF

Automatic installation complete. As the next steps, you should:

1. Start the server: systemctl start problem-list-nginx
   The web interface should then be reachable at http://this-server:${PORT}.

2. Enable the service to start automatically: systemctl enable problem-list-nginx
EOF
