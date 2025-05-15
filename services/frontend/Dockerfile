FROM nginx:alpine

RUN apk add --no-cache gettext

WORKDIR /usr/share/nginx/html

COPY src/index.html.template .
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD envsubst '${BACKEND_URL}' < index.html.template > index.html \
    && nginx -g 'daemon off;'