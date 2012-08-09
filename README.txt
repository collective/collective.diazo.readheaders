.. contents::

Introduction
============

"What's Diazo?", I hear you say.  From `diazo.org <http://diazo.org>`_:

    Diazo allows you to apply a theme contained in a static HTML web page to a
    dynamic website created using any server-side technology. With Diazo, you
    can take an HTML wireframe created by a web designer and turn it into a
    theme for your favourite CMS, redesign the user interface of a legacy web
    application without even having access to the original source code, or
    build a unified user experience across multiple disparate systems, all in a
    matter of hours, not weeks.

    When using Diazo, you will work with syntax and concepts familiar from
    working with HTML and CSS. And by allowing you seamlessly integrate XSLT
    into your rule files, Diazo makes common cases simple and complex
    requirements possible.

About this package
==================

This package extends the standard theming middleware of Diazo to add the
ability to read the location of a rules XML file from the WSGI environment.
This means, amongst being able to read a rules location from the environment
for the local user, that an upstream service (such as a web server, reverse
proxy, caching proxy, etc) is able to control the theme the middleware is using
-- and change this for any given request.  This contrasts with the
configuration-based approach taken by Diazo's standard middleware, which
requires a fixed path to be specified for the middleware.

So, this means with the right WSGI configuration, you could conceivably have
one Diazo instance serving any number of themes without needing to explicitly
configure paths, urlmaps or the like.  If you combine this with a suitable
front-facing tool (such as a configurable web server like Apache, Nginx,
Cherokee, or any other), then you can have this one Diazo instance theming any
number of applications, and theming differently based upon any condition your
web server supports -- such as incoming host name, HTTP vs HTTPS, specific URLs
or regex, headers, IP addresses, and more.  To achieve this, all you need to do
is set the right HTTP header -- which is the path to your rules file -- and
ensure this is sent to your middleware based upon your various conditions.

Example
=======

In this example, we can deploy this extended Diazo middleware to act as a
one-size-fits-all theming backend behind our web server. With the right
WSGI pipeline, we can have one WSGI pipeline servicing as many backends 
as you like, serving any number of different themes, all without any explicit
WSGI configuration.  Keep in mind the potential of header spoofing - exercise
extreme care.

WSGI pipeline
-------------

Prepare a configuration for PasteScript as follows::

    [server:main]
    use = egg:Paste#http
    host = 0.0.0.0
    port = 5000

    [composite:main]
    use = egg:Paste#urlmap
    / = default

    [pipeline:default]
    pipeline = theme
               proxy

    [filter:theme]
    use = egg:collective.diazo.readheaders
    #You can use any other Diazo middleware options here, too!
    read_network = True
    debug = True

    [app:proxy]
    use = egg:djb.headerproxy

Over the standard Diazo/WSGI configuration seen at
http://docs.diazo.org/en/latest/quickstart.html keen-eyed viewers will notice
the following:

#. We use ``collective.diazo.readheaders`` instead of ``diazo`` - this
   allows the ``X-Diazo-Rules`` header to be read from the incoming WSGI
   environment and used as the traditional ``rules`` option. This means
   that any format the ``rules`` option accepts (such as network-based URLs)
   will work if set as this header. In the specific case of network URLs, you
   will need to configure ``read_network`` to be enabled.
   
   This section automatically accepts any and add options that Diazo does: see
   http://docs.diazo.org/en/latest/deployment.html#wsgi - and we demonstrate
   this above. 

#. We use the special WSGI proxy `djb.headerproxy
   <http://pypi.python.org/pypi/djb.headerproxy>`_ which will reverse proxy to
   an arbitrary location based upon incoming headers. By comparison, the
   standard Paste proxy requires an explicitly defined address in the
   configuration. As per the documentation for ``djb.headerproxy``, the headers
   upstream are, by default, expected to be ``X-Proxy-Force-Host`` and 
   ``X-Proxy-Force-Scheme`` -- this mapping is configurable, however.

Front-end
---------

Now, in our front-end server, we can configure our reverse proxy and
set the headers accordingly.  For instance, with Apache you might do the
following::

    RequestHeader set "X-Diazo-Rules" "/path/to/rules.xml"
    RequestHeader set "X-Proxy-Force-Host" "app-server.example.com:8080"
    RequestHeader set "X-Proxy-Force-Scheme" "http"
    RewriteRule / http://localhost:5000 [L,P]

In which, the rewrite rule points to the location of the service running
the above Paste WSGI configuration.  

Don't forget that the ``X-Diazo-Rules`` option will be interpreted on the
local machine running the WSGI pipeline. So, if you refer to a local file
it will be local to *that machine*. This point is moot if you are running
Diazo on the same machine - but it should still be emphasised.  Keep in 
mind too that you can configure options like this::

    RequestHeader set X-Diazo-Rules "http://example.com/path/to/rules.xml"

and they will work as well (assuming, at least in this case, that your
middleware has the ``read_network`` option enabled).

Deployment options
^^^^^^^^^^^^^^^^^^

You can deploy using your choice of server -- it doesn't need to be Paste.
Similarly, you can deploy with your choice of front-end -- it certainly doesn't
need to be Apache.  If you've deployed something similar to the above, then
consider contributing your deployment configuration here!

Cherokee, uWSGI and Pip/Buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One successful deployment utilises the `Cherokee web server
<http://cherokee-project.com/>`_ and `uWSGI <http://projects.unbit.it/uwsgi/>`_
and runs uWSGI using a local socket on the web server machine. Cherokee (much
like Ngnix) can talk directly to uWSGI, which in turn is able to directly
utilise Paste-style ini configuration, like the one above.  For uWSGI, the only
addition configuration needed was to add this to the top of the ini file::

    [uwsgi]
    home = /opt/diazo
    processes = 8
    vacuum = true
    master = true
    socket = %(home)/var/uwsgi.sock
    pythonpath = %(home)/eggs/*.egg
    pythonpath = %(home)/src/*

and then uWSGI, which was simply installed along with all dependencies thus::

    cd /opt/diazo
    virtualenv .
    source bin/activate
    pip install uwsgi collective.diazo.readheaders djb.headerproxy

can be easily started using::

    ./bin/uwsgi --ini-paste diazo.ini

which reads its own options from the configuration, together with the WSGI
pipeline and associated config.  For bonus points, you can also deploy the
above with `Buildout <http://www.buildout.org/>`_ too::

   [buildout]
   parts = lxml instance
   eggs-directory = eggs

   [lxml]
   recipe = z3c.recipe.staticlxml
   egg = lxml

   [instance]
   recipe = zc.recipe.egg
   eggs =
       collective.diazo.readheaders
       djb.headerproxy
       uwsgi
   dependent-scripts = true

Phew!

Contributing
============

Join in at https://github.com/collective/collective.diazo.readheaders --
if you're already a member of the Collective then you can already push changes.
Otherwise, fork away and send a pull request.
