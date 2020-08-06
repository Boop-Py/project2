from django import forms

class Comment_Form(forms.Form):
    comment = forms.CharField()


class Bid_Form(forms.Form):
    bid = forms.IntegerField()
