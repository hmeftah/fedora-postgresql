FROM fedora:latest 
MAINTAINER Herve Meftah <rv.meftah@gmail.com>

# common packages
RUN yum -y update; yum clean all
RUN yum -y install sudo epel-release; yum clean all
RUN yum -y htop; yum clean all
RUN yum -y groupinstall "Development Tools"

#install fabric
yum -y install python-pip ; yum clean all
RUN pip install fabric

# install sshd
RUN yum -y install openssh-server net-tools wget ; yum clean all

RUN mkdir -p /var/run/sshd
RUN echo "root:password" | chpasswd
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
RUN sed -i 's/session   required        pam_loginuid.so/session         optional        pam_loginuid.so/g' /etc/pam.d/sshd

EXPOSE 22
ENTRYPOINT ["/usr/sbin/sshd"]
