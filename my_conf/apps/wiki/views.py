from django.http import HttpResponse


def project_list(request):
    return HttpResponse('Список проектов')
