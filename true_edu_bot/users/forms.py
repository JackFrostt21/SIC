# ###V1
# from django import forms
# from django.contrib.auth.models import Group
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# from .models import CustomUser

# class CustomUserCreationForm(UserCreationForm):
#     Group = forms.ModelChoiceField(queryset=Group.objects.all())

#     class Meta(UserCreationForm):
#         model = CustomUser
#         fields = '__all__' # удалить не нужное

# class CustomUserChangeForm(UserChangeForm):
    
#     class Meta(UserChangeForm):
#         model = CustomUser
#         fields = '__all__' # удалить не нужное
# ###V1

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = '__all__'

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = '__all__'
