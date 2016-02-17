from django import forms
import autocomplete_light


class SearchAutocomplete(autocomplete_light.AutocompleteListBase):
    choices = ['ABC', 'Apple', 'Ajax']

autocomplete_light.register(SearchAutocomplete)

# Using widgets directly in any kind of form.
class SearchBarForm(forms.Form):
#    user = forms.ModelChoiceField(User.objects.all(),
#            widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))

#    cities = forms.ModelMultipleChoiceField(City.objects.all(),
#            widget=autocomplete_light.MultipleChoiceWidget('CityAutocomplete'))

    textField = forms.CharField(
            widget=autocomplete_light.TextWidget('SearchAutocomplete'))


