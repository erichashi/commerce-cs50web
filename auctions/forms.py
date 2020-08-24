from django import forms

class placeBid(forms.Form):
    bid = forms.IntegerField(label="Place your bid")
    

class placeComment(forms.Form):
    content = forms.CharField(label="Leave your comment")

