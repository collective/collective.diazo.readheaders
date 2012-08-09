from diazo.wsgi import DiazoMiddleware, asbool

DIAZO_RULES_HEADER = 'HTTP_X_DIAZO_RULES'

class ExtendedDiazoMiddleware(DiazoMiddleware):
    
    def __init__(self, *args, **kw):
        """Initialise the extended Diazo middleware.

        By default, we read the Diazo rules location from
        the headers if they are present in the environment.
        Sanitise the headers at the door or prepare for unforeseen
        consequences!
        """
        if not 'rules' in kw:
            kw['rules'] = None
        self.read_headers = asbool(kw.get('read_headers', 'true'))

        super(ExtendedDiazoMiddleware, self).__init__(*args, **kw)

    def __call__(self, environ, start_response):
        #Read certain options from headers but only if allowed
        if self.read_headers:
            if DIAZO_RULES_HEADER in environ:
                self.rules = environ[DIAZO_RULES_HEADER]

        if not self.rules:
            raise ValueError('No rules specified in settings or headers.')

        return super(ExtendedDiazoMiddleware, self).__call__(environ,
                                                             start_response)
