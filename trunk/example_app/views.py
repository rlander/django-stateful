from django_stateful.views import StatefulView, Page, FinalPage, show_page
from django import forms
from datetime import datetime
from itertools import count

class Counter(StatefulView):
    def main(self):
        for c in count():
            yield Page("you've been here %s times before" % c)

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

        