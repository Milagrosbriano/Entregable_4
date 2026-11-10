# syntax=docker/dockerfile:1

FROM node:22-alpine AS builder

WORKDIR /build

COPY index.html v1.html styles.css app.js config.docker.js ./

RUN node --check app.js \
    && node --check config.docker.js \
    && mkdir /dist \
    && cp index.html v1.html styles.css app.js /dist/ \
    && cp config.docker.js /dist/config.js


FROM nginx:1.28-alpine AS runtime

COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /dist/ /usr/share/nginx/html/

USER 101:101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
