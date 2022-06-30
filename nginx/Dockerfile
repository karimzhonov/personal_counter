FROM nginx:1.21-alpine

ENV TZ="Europe/Moscow"
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d