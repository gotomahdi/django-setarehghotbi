from django import forms
from .models import TicketModel,Comment


class TicketForm(forms.ModelForm):
	class Meta:
		model=TicketModel
		fields=['title','message']




class CommentForm(forms.ModelForm):
    content = forms.CharField(label ="", widget = forms.Textarea(
    attrs ={
        'class':'form-control',
        'placeholder':'میتونید دیدگاه خودتون رو اینجا بنویسید!',
        'rows':7,
        'cols':103,
        'maxlength':1000,
    }))


    class Meta:
    	model=Comment
    	fields=['content']