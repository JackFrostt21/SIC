from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "testapp/index.html"
    context_object_name = "latest_question_list"


class DetailView(generic.DetailView):
    model = Question
    template_name = "testapp/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "testapp/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "testapp/detail.html", {
            "question": question,
            "error_message": "Вы не выбрали вариант.",
        })
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("testapp:results", args=(question.id,)))