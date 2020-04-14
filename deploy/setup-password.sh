# Create the basic auth password
#
# Run inside the nginx container to avoid requiring any additional tools on the server
apk update
apk add apache2-utils
cat | htpasswd -i -c /htpasswd "$USER"
