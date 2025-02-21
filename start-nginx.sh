#!/bin/bash
# Substitute environment variables in the Nginx config file
envsubst '$DOMAIN_NAME' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
# Start Nginx
nginx -g "daemon off;"
