from django.conf.urls.defaults import *
from views import Wizard, Counter

urlpatterns = patterns('',
    url(r'^counter/$', Counter.handle, name='counter'),
    url(r'^wizard/$', Wizard.handle, name='wizard'),
)
