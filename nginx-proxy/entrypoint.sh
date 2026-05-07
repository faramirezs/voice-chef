#!/bin/sh
set -e

DOMAIN_NAME="${DOMAIN_NAME:=localhost}"

mkdir -p /etc/nginx/ssl

if [ ! -f /etc/nginx/ssl/nginx.crt ]; then
		echo "Generating self-signed certificate for ${DOMAIN_NAME}..."
		# Detect IP vs hostname so the SAN uses the correct prefix (IP: or DNS:)
		if echo "$DOMAIN_NAME" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
			SAN="IP:${DOMAIN_NAME},IP:127.0.0.1"
		else
			SAN="DNS:${DOMAIN_NAME},IP:127.0.0.1"
		fi
		openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
			-keyout /etc/nginx/ssl/nginx.key \
			-out /etc/nginx/ssl/nginx.crt \
			-subj "/CN=${DOMAIN_NAME}" \
			-addext "subjectAltName=${SAN}"
		chmod 600 /etc/nginx/ssl/nginx.key
		chmod 644 /etc/nginx/ssl/nginx.crt
		echo "Certificate generated."
else
	echo "Existing certificate found, skipping generation."
fi

echo "Testing nginx configuration..."
nginx -t

echo "Starting nginx..."
exec nginx -g "daemon off;"
