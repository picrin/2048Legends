FROM debian:wheezy

MAINTAINER Adam Kurkiewicz "adam@kurkiewicz.pl"

RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
RUN echo "deb http://nginx.org/packages/mainline/debian/ wheezy nginx" >> /etc/apt/sources.list

ENV NGINX_VERSION 1.7.6-1~wheezy

RUN apt-get update && apt-get install -y nginx=${NGINX_VERSION}
RUN rm -fr /etc/nginx/conf.d
RUN mkdir -p /var/www/html/static/css
RUN mkdir -p /var/www/html/static/js
COPY nginx.conf /etc/nginx/nginx.conf
COPY css/ /var/www/html/static/css
COPY js/ /var/www/html/static/js
RUN ls /var/www/html/static
#RUN chmod 0444 /var/www/html/static/css/*
#RUN chmod 0444 /var/www/html/static/js/*

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

VOLUME ["/usr/share/nginx/html"]
VOLUME ["/etc/nginx"]

EXPOSE 80 8000

CMD ["nginx", "-g", "daemon off;"]
