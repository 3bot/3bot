# 3bot
> Configure, Build and Perform

## Contents

* [About 3bot](#about-3bot)
    * [Build](#about-3bot-build)
    * [Configure](#about-3bot-configure)
    * [Perform](#about-3bot-perform)
* [Using 3bot](#using-3bot)
    * [Use the hosted version of 3bot](#using-3bot-hosted)
    * [Run your own  3bot instance](#using-3bot-own)
        * [Installation](#using-3bot-own-installation)
* [Support](#support)



  
<a name="about-3bot"></a>
## What 3bot does and why you should use it

The story .. 

3bot is a system administration toolkit developed by arteria GmbH over last years. Started as a collection of shell scripts that turned into a Django app that could create other reusable apps, Django projects and deploy code using git and fabric on remote machines 





At [arteria](https://www.arteria.ch) we believe that everyone should be able to do more with less time by automating repetitive task and that work could be done by every team member. Avoid bottle necks where possible. 


3bot is not a... .. 

3bot is build to build, to configure and to perform task.

Easy to integrate into already /legacy / build systems  like jenkins

<a name="about-3bot-build"></a>
### Build 
With «build» in the general meaning is ment to 

 * building apps, 
 * building projects, 
 * .. 

<a name="about-3bot-configure"></a>
### Configure 
Even if 3bot is not a configuration managment system in the classic way, 3bot can be used to setup and configure    a remote machine (server, .. ) etc.


<a name="about-3bot-perform"></a>
### Perform

To «perform» is the general term for executing tasks by running workflows.
There are a lot of built-in task that can be used and adapted or you could use tasks from the market place. ~~to perform and/ or remote execuring, tasks. ~~


## How is behind 3bot

3bot was written by Philippe O. Wagner and shaped by Walter Renner.  ... and is developed and maintained by arteria GmbH. 

Walter Renner is the maintainer of the 3bot platform.
  
## How 3bot is licensed
Anyone is free to use or modify this software under ther terms of the BSD license.

<a name="using-3bot"></a>
## How to use 3bot
3bot is simple to get up and running and fairly powerful to use! 
A worker must be installed and configured on each machine. 
These workers can be connected to the hosted/cloud based version of 3bot or your own self-hosted instance.

<a name="using-3bot-hosted"></a>
### Use the hosted version of 3bot - it's free!
~~3bot in the cloud~~
You could create an user account for you and use 3bot with your team at [my.3bot.io](https://my.3bot.io) and run  workflows from the latest and greatest, stable version of 3bot directly from the could for free! 

<a name="using-3bot-own"></a>
### How to run your own self-hosted 3bot instance
#### Should I use the self hosted version?
As developer, of course, run your own version to integrate new features, ..
##### Pros :
* Works for your intranet /behind a firewall.
* Works in your intranet - no Port forwarding, fixed IP, NAT, .. required.
* 

##### Cons:
* no market place access. ()but you could export and import ... 
* Set up, back up and maintain your own system.


<a name="using-3bot-own-installation"></a>
#### Installation

To get 3bot up and running, make sure you have [pip](https://github.com/pypa/pip) and [virtualenv](https://github.com/pypa/virtualenv) installed on your system to be able to run the following commands in your terminal.

    virtualenv --no-site-packages -p python 3bot && cd 3bot

    source ./bin/activate

    pip install django==1.7

    pip install threebot
    pip install threebot-organizations

    django-admin startproject djangothreebot
    cd djangothreebot

Add ``sekizai``, ``threebot``, ``organizations`` to your ``INSTALLED_APPS`` in your project settings.

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
		'django.contrib.sites',
        
        'sekizai',
        'threebot',
        'organizations',
    )

Make sure that all ``django.contrib.X`` apps are installed as well.


Add ``sekizai.context_processors.sekizai``, ``request`` and ``auth`` to ``TEMPLATE_CONTEXT_PROCESSORS`` in your project settings.

    TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.request",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.tz",
        "django.contrib.messages.context_processors.messages",
        "sekizai.context_processors.sekizai", )

3bot provides a login form, to use it properly, add the following lines to your settings.py file
    
    LOGIN_URL = '/login/'
    LOGIN_REDIRECT_URL = '/'

Set the ``SITE_ID = 1`` as well. Change 'example.com' using the [admin](/admin/sites/site/1/) for your needs.

Add the urls patterns for ``teams`` and ``threebot`` to your root urls.py 


    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('threebot.urls')),
        url(r'^teams/', include('organizations.urls')),
    )

After all modifications are done, do not forget to sync your database. 

    python manage.py syncdb
    python manage.py migrate

Start the development server and enjoy your fresh 3bot instance running under [http://127.0.0.1:8000](http://127.0.0.1:8000).

    python manage.py runserver


<a name="support"></a>
## How to get help or support


### Looking for commercial support
 
### Knowledge Base

Browse through the Knowledge Base on [my.3bot.io/kb](https://my.3bot.io/kb/). 

### Mailing list
TODO

 

## How to get involved

### Submit ideas and feature requests
Have a brilliant idea or are you missing a feature? Feel free to create an [issue on Github](https://github.com/3bot/3bot/issues/new) or send us a message using the contact form on the [3bot website](http://3bot.io). 

### Contributing and developing

If you want to be part of the 3bot community and help to evolve this platform ...

  

## System requirements

* Name, version, description, and/or features of the program.
* Install, uninstall, configuration, and operating instructions.
* Credit, acknowledgments, contact information, and copyright.
* License
* Known bugs and a change log.

## Change Log

### Public Beta
We're currently here. Want to join us? 

### Private Beta
We did that as well.

### Private Alpha
We did that.


## Issue Tracking
Please use the [issue tracker on Github](https://github.com/3bot/3bot/issues/new) to file a bug. 


## Technical detail and remarks

~~Transport:
packed, compresed and encrypted
~~

### Credentials and Security

* SSL/TLS transport in protection is highly recommended!  
* The transmitted data between 3bot and the 3bot worker are packed and encrypted by default. 
* Do never share your credentials, API token or secret keys.

### Technology used

* Python 
* ZeroMQ
* https://www.dlitz.net/software/pycrypto/  https://github.com/dlitz/pycrypto





## The 3bot worker
### Worker Hacks
* build and connect your own worker /fork
* Combine with alogator
* Install a bidirectional worker for monitoring this and that
* 