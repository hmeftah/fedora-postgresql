#!/usr/bin/env python

from __future__ import with_statement
from fabric.api import env,hide,settings,execute
from fabric.operations import run, get, put, sudo
from fabric.contrib.files  import  sed
import datetime
import os,netrc

working_path = os.getcwd()

def localhost():
	env.hosts ='localhost' 
	env.port = 49160   # port number set when starting your fedora docker container
	env.user ='root' 
	env.password = 'password'

def get_os_version():
	''' Get the OS version of the remote host'''
	with hide('running','warnings'), settings (warn_only=True):
		version = run('cat /etc/*-release | grep DISTRIB_ID' )
		if  len(version) == 0 :
			version = run('cat /etc/*-release | grep PRETTY_NAME' )
		        if len(version) == 0 :
				version = run('cat /etc/redhat-release')
		print version
		return version

def install_postgresql():
	''' compile postgresql from sources as production-like server 
	    flags has been set to allow openssl, selinux python and dtrace entries within the server
	'''
	with hide('running','warnings'), settings (warn_only=True):
		''' Compile the latest version of postgresql'''
	        start_time = datetime.datetime.now()	
		run('mkdir -p /home/environment/sourcepackages')
		run('mkdir -p /opt/pg941')
		run('cd /home/environment/sourcepackages && wget -q http://ftp.postgresql.org/pub/source/v9.4.1/postgresql-9.4.1.tar.gz \
		     -O /home/environment/sourcepackages/postgresql-9.4.1.tar.gz')
		run('mkdir -p /home/environment/build')
		run('cp /home/environment/sourcepackages/postgresql-9.4.1.tar.gz /home/environment/build')
		run('cd /home/environment/build && tar -zxvf /home/environment/sourcepackages/postgresql-9.4.1.tar.gz')
                run('cd /home/environment/build/postgresql-9.4.1 && /home/environment/build/postgresql-9.4.1/configure \
                                        --prefix=/opt/pg941 --with-openssl --with-selinux --with-python --enable-dtrace')
		nproc = run ('nproc')
		run('cd /home/environment/build/postgresql-9.4.1 && make -j%s' % nproc)
		run('cd /home/environment/build/postgresql-9.4.1/contrib  && make -j%s' % nproc)
		run('cd /home/environment/build/postgresql-9.4.1 && make check')
		run('cd /home/environment/build/postgresql-9.4.1 && make install')
		
		run('cd /home/environment/build/postgresql-9.4.1/contrib/start-scripts && cp linux /etc/init.d/postgresql')
		run('cd  /etc/init.d/ && chmod +x postgresql')
		end_time =  datetime.datetime.now()
                print "Elapsed time : %s " % (end_time-start_time)

def init_postgresql():
	''' Create postgresql database, set character set encoding and data directory
	    set start up script		        
	'''
	with hide('running','warnings'), settings (warn_only=True):
		run ('/etc/init.d/postgresql stop',  user='root', shell = False)
		postgres = sudo('cat /etc/passwd | grep postgres', user='root', shell = False )
		run ('adduser postgres', user='root', shell = False)
		run ('mkdir /opt/pgsql/data -p' , user='root', shell = False)
		run ('chown postgres:postgresl /opt/pgsql/data', user='root', shell = False)	
		run ("/usr/local/pgsql/bin/initdb  -E unicode -k \
		      -D /opt/pgsql/data", user='postgres' ,shell= False)
		sed('/etc/init.d/postgresql', 'PGDATA="/usr/local/pgsql/data"', 'PGDATA="/opt/pgsql/data/"', 
                     use_sudo=True, shell=False)
		result  = execute(get_os_version)
                version = result.get(env.host_string)
                if version.find('Ubuntu') >0 :
                        run("/etc/init.d/postgesql restart",  user='root', shell = False)
                elif version.find('Fedora')>0:
                        run('systemctl enable postgresql.service' ,user='root' , shell = False)
			run('systemctl start postgresql.service' ,user='root' , shell = False)
		run ('/etc/init.d/postgresql start')
		

def set_UTC_timezone():
         with hide('running','warnings'), settings (warn_only=True):
		sudo('rm /etc/localtime')
                sudo('ln -s /usr/share/zoneinfo/Etc/UTC /etc/localtime')
		result  = execute(get_os_version)
		version= result.get(env.host_string)
		#version = result(env.hosts[0])
		#print version
	        if version.find('Ubuntu') >0 :
                	sudo("service cron restart",  user='root', shell = False)
		elif version.find('Fedora')>0:
			sudo('systemctl restart crond.service' ,user='root' , shell = False)
		run('date')
		
