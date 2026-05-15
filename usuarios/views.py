from django.shortcuts import render,redirect
from .forms import CadastroForm

def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calculadora')   # volta pra calculadora após cadastro
    else:
            form = CadastroForm()
    return render(request,'usuarios/cadastro.html',{'form':form})