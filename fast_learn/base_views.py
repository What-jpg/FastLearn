from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http.response import HttpResponse
from django.shortcuts import render

@login_required
@require_GET
def home_view(request):
    return render(request, "index.html")

def health_view(request):
    return HttpResponse("OK")