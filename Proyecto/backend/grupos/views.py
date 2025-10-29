from django.shortcuts import render, get_object_or_404
from .models import Grupo

def grupo_detail(request, pk=1):
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, "grupos/grupo_detail.html", {"grupo": grupo})
