from django.http import HttpResponse
from django.shortcuts import render_to_response as show_page
from django.conf import settings
from datetime import datetime, timedelta
from threading import Thread
import time

__all__ = ['StatefulView','Page','FinalPage','show_page']

class Page(HttpResponse): pass
class FinalPage(HttpResponse): pass

class StatefulViewType(type):
    def __init__(cls, name, bases, dct):
        LIVING_STATES = {}
        cls._LIVING_STATES = LIVING_STATES
        delta = timedelta(seconds=settings.CLEAN_STATES_SECONDS)
        def clean_threads():
            while True:
                for k,(s,updated) in LIVING_STATES.items():
                    if updated + delta < datetime.today():
                        try:
                            del LIVING_STATES[k]
                        except KeyError:
                            pass
                time.sleep(settings.CLEAN_STATES_SECONDS)
        t = Thread(target=clean_threads)
        t.daemon = True
        t.start()

class StatefulView(object):
    __metaclass__ = StatefulViewType
    
    @classmethod
    def handle(cls, request, *a, **kw):
        keyname = str(cls)+'_'+request.session.session_key
        states = cls._LIVING_STATES
        
        if keyname in states:
            gen,x = states[keyname]
            response = gen.send((request, a, kw))
        else:
            gen = cls().main()
            response = gen.next()
                    
        if isinstance(response, FinalPage):
            del states[keyname]
        else:
            states[keyname] = (gen, datetime.now())
        
        return response
    
    def main(self, request, *a, **kw):
        raise NotImplementedError("%s must implement 'main'" % self.__class__.__name__)

