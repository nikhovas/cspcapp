from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.core.handlers.wsgi import WSGIRequest
from .utilities import reformat_request_get_params, overview_get_format
from django.contrib.auth.decorators import login_required

@login_required
def student_add_function(request: WSGIRequest) -> HttpResponse:
    return render(request, 'student_add.html')
