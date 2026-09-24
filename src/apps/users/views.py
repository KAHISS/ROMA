import environ

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.users.forms import UserForm, UserPasswordForm, UserUpdateForm
from apps.users.services import (
    create_user,
    delete_user,
    get_user_list_context,
    update_user,
    update_user_password,
)
from django.contrib.auth import get_user_model

User = get_user_model()

env = environ.Env()

PER_PAGE = env.int("PER_PAGE", default=12)


@login_required
def user_list(request):
    form = UserForm()
    password_form = None

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")

        if action == "delete":
            try:
                delete_user(user_id)
                return redirect("users:list_users")
            except User.DoesNotExist:
                form.add_error(None, "O usuário selecionado não foi encontrado.")

        elif action == "set_password":
            try:
                user_instance = User.objects.get(pk=user_id)
                password_form = UserPasswordForm(user_instance, request.POST)
                user = update_user_password(password_form)
            except User.DoesNotExist:
                password_form = UserPasswordForm(request.user, request.POST)
                password_form.add_error(None, "O usuário selecionado não foi encontrado.")
                user = None

            if user is not None:
                return redirect("users:list_users")

        else:
            if user_id:
                try:
                    user_instance = User.objects.get(pk=user_id)
                    form = UserUpdateForm(request.POST, instance=user_instance)
                    user = update_user(user_id, form)
                except User.DoesNotExist:
                    form = UserUpdateForm(request.POST)
                    form.add_error(None, "O usuário selecionado não foi encontrado.")
                    user = None
            else:
                form = UserForm(request.POST)
                user = create_user(form)

            if user is not None:
                return redirect("users:list_users")

    if password_form is None:
        password_form = UserPasswordForm(request.user)

    context = get_user_list_context(request, PER_PAGE)
    context.update({
        "form": form,
        "password_form": password_form,
        "title": "Usuários",
        "page": "users",
    })

    return render(request, "users/pages/users.html", context)
