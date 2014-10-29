
FROM centos:centos7
MAINTAINER Adam Kurkiewicz "adam@kurkiewicz.pl"

RUN yum -y update; yum clean all
RUN yum -y install epel-release
RUN yum -y install python-pip

COPY WC2048/ /home/centos/WC2048/
COPY website/ /home/centos/website/
COPY templates/ /home/centos/templates/
COPY startgunicorn.sh /home/centos/
COPY requirements.txt /home/centos/
RUN touch /home/centos/isDebug && echo "0" > /home/centos/isDebug
RUN pip install -r /home/centos/requirements.txt
EXPOSE 8000
RUN chmod +x /home/centos/startgunicorn.sh
#CMD ["/bin/bash", "/home/centos/startgunicorn.sh"]
WORKDIR home/centos/
CMD ["gunicorn", "WC2048.wsgi:application", "127.0.0.1:8000"]
