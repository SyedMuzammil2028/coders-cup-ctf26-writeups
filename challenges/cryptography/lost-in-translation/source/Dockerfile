FROM nginx:stable-alpine
RUN apk add --no-cache python3 \
    && mkdir -p /opt/challenge \
    && rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
COPY generate.py /opt/challenge/generate.py
COPY entrypoint.sh /opt/challenge/entrypoint.sh
COPY website/ /usr/share/nginx/html/
# Apply the read-only permissions first, then restore execution permission on
# the container entrypoint.  ``a=rX`` can otherwise strip it during the
# recursive pass, preventing Docker from starting the image as the nginx user.
RUN chmod -R a=rX /usr/share/nginx/html /opt/challenge \
    && chmod 0555 /opt/challenge/entrypoint.sh
USER nginx
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/healthz || exit 1
ENTRYPOINT ["/opt/challenge/entrypoint.sh"]
