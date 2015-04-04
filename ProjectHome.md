# What is it? #

A revolutionary approach to web applications using [django](http://www.djangoproject.com). Code your views using linear flow logic, maintaining the state across requests. Similar to [UnCommon web](http://common-lisp.net/project/ucw/index.html), [Seaside](http://www.seaside.st/) and [Borges](http://borges.rubyforge.org/)

Since its just another django app, you can still write some views in the traditional style, and use all the features of django web framework.

the other home of this project is http://woobiz.com.ar/en/articles/stateful-django

# The kind of code you end up writing: #

A counter:
```
class Counter(StatefulView):
    def main(self):
        for c in count():
            yield Page("you've been here %s times before" % c)
```

A wizard (kind of):
```
class NameForm(forms.Form):
    name = forms.CharField(max_length=100)
    
class LanguageForm(forms.Form):
    langs = [(x,x) for x in ['python','perl','ruby','php','prolog']]
    lang = forms.ChoiceField(choices=langs, initial='python', widget=forms.RadioSelect)
    
class Wizard(StatefulView):
    def main(self):
        started = datetime.now()
        
        form = NameForm()
        name = None
        while not name:
            input, a, kw = yield show_page('ask_name.html', {'form': form,})
            form = NameForm(input.GET)
            if form.is_valid():
                name = form.cleaned_data['name']
                
        form = LanguageForm()
        input, a, kw = yield show_page('ask_language.html', {'form': form, 'name':name})
        form = LanguageForm(input.GET)
        
        if form.is_valid():
            lang = form.cleaned_data['lang']
            if lang == 'python':
                yield Page("Cool, now refresh and see how much time you spent in this wizard")
            else:
                yield FinalPage("well %s, i guess you should look for a %s framework then..." % (name,lang))
        else:
            yield FinalPage("hey, you are not going with the flow you know, goodbye %s." % name)
        
        delta = datetime.now() - started
        yield FinalPage("You spent %s seconds, bye %s !!" % (delta.seconds, name))

```

# Implementation facts: #

  * Stores generators in memory to achieve statefulness.

  * Uses request.session.session\_key to tell visitors apart.

  * A different thread takes care of cleaning up 'old' generators.

  * Requires the server to run in a single process. (a better implementation could use a separate storage for 'living' generators, or serializable tasklets like twisted's)

  * Mostly experimental, yet small intranet applications could use it right away.



# Installation, requirements and usage #
## Quick and dirty ##
Just checkout trunk, edit reelevant paths in settings.py and run:
```
python manage.py runserver <host>:<port>
```
then play around with example\_app/views.py

## Long version ##
  * Checkout django\_stateful

  * Add the following to your settings.py (or use the one from the repository):
    * SESSION\_SAVE\_EVERY\_REQUEST = True #_this forces session\_keys even for anonymous users_
    * CLEAN\_STATES\_SECONDS = 60 #_this checks every 60 seconds if any stored state is over 60 seconds old, thus the oldest a state can be is around 60\*2 seconds_

  * import the following things:
> > ` from django_stateful.views import StatefulView, Page, FinalPage, show_page `

  * Define a class that would be your view, inheriting from StatefulView and redefine its 'main' method

  * Inside the 'main' method:
    * If you want to show a page to the user, you can yield a Page (which is no more than a clean subclass of HttpResponse), like this:
> > ` yield Page("here's something the server wants to say") `
    * If you want to render a template to the user, use 'show page', its just an alias for render\_to\_response, like this:
> > ` yield show_page('template.html', {'foo': foo, 'bar':bar}) `
    * Apart from yielding an HttpResponse, every yield statement recieves the request, args and kwargs from the url dispatching mechanism, so in cases where you want to use those (for instance, when showing a form and waiting for the user to submit it), you can use the following idiom:
> > ` input, args, kwargs = yield show_page('ask_for_input.html', {'form': form}) `

  * When you're done with coding your view, you import it from your urls.py file then set your class 'handle' classmethod as the target for the dispatching mechanism, like this:
```
from django.conf.urls.defaults import *
from my_project.views import MyCustomView

urlpatterns = patterns('',
    url(r'^my_custom_view/$', MyCustomView.handle),
)
```