from tokenize import Comment
from django import forms
from newspaper.models import Comment, Contact

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = "__all__"
       

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["post", "content"]