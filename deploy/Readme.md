# Deploy

Tools to set up hosting for the problem list on a server.
The setup process is automated using `setup.sh`.
Running it will:
  * Add a systemd unit controlling an nginx instance running in a docker container.
    Nginx will serve the static files of the problem list
  * Set up a basic authentication user and password to protect access to the nginx server.
    The `htpasswd` file containing the details will also be protected from normal access.
  * Create a deploy user and give it access to the static html file directory.
    This user can be used to push updated problem list files, for example from a CI job.
    The user won't have a password set, but an authorized public key for ssh logins will be added during the setup.
