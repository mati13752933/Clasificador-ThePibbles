from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, PerfilUpdateForm, CustomPasswordChangeForm

@login_required
def perfil(request):
    return render(request, 'perfil.html')

@login_required
def editarPerfil(request):
    if request.method == "POST":

        if "guardar_perfil" in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            perfil_form = PerfilUpdateForm(request.POST, request.FILES, instance=request.user.perfil)
            password_form = CustomPasswordChangeForm(request.user)

            if user_form.is_valid() and perfil_form.is_valid():
                user_form.save()
                perfil_form.save()
                return redirect("perfil")

        elif "cambiar_password" in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            perfil_form = PerfilUpdateForm(instance=request.user.perfil)
            password_form = CustomPasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                usuario = password_form.save()
                update_session_auth_hash(request, usuario)
                return redirect("perfil")

    else:
        user_form = UserUpdateForm(instance=request.user)
        perfil_form = PerfilUpdateForm(instance=request.user.perfil)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

    return render(request, "editarPerfil.html", {
        "user_form": user_form,
        "perfil_form": perfil_form,
        "password_form": password_form
    })


