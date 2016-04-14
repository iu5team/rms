from django.shortcuts import render


def index(request):
    """
    Some desc
    :param request:
    :return:
    """
    ctx = {}
    return render(request, 'index.html', ctx)
