FROM nginx:1.28-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html v1.html styles.css app.js /usr/share/nginx/html/
COPY config.docker.js /usr/share/nginx/html/config.js
USER 101:101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
