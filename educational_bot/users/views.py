###V1
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import Group

from educational_bot.users.forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('homepage')
    template_name = 'users/signup.html'

    # def post(self, request, *args, **kwargs):
    #     form = CustomUserCreationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.save()
              
    #         #One user Group
    #         user_group = Group.objects.get(name=form.cleaned_data['groups'])
    #         user.groups.add(user_group)

    #         #Multiple user Groups
    #         for form_ug in form.cleaned_data['groups']:
    #             user_group = Group.objects.get(name=form_ug.name)
    #             user.groups.add(user_group)
    #         return redirect('homepage')
    #     else:
    #         return render(request, self.template_name, {'form': form})
###V1