from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Aluno, Curso

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

        widgets = {
            'password': forms.PasswordInput(),
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['user', 'curso', 'ano']

    user_form = UserForm()

    def __init__(self, *args, **kwargs):
        super(AlunoForm, self).__init__(*args, **kwargs)
        self.fields.update(self.user_form.fields)
        self.initial.update(self.user_form.initial)

    def is_valid(self):
        return super(AlunoForm, self).is_valid() and self.user_form.is_valid()

    def save(self, commit=True):
        user = self.user_form.save(commit=False)
        user.save()
        aluno = super(AlunoForm, self).save(commit=False)
        aluno.user = user
        if commit:
            aluno.save()
        return aluno