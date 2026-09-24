from django.http import Http404
import environ

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.users.forms import LoginForm, UserForm, UserPasswordForm, UserUpdateForm
from apps.users.services import (
    authenticate_and_login,
    create_user,
    delete_user,
    get_user_list_context,
    update_user,
    update_user_password,
    logout_user
)
from django.contrib.auth import get_user_model

User = get_user_model()

env = environ.Env()

PER_PAGE = env.int("PER_PAGE", default=12)


@login_required
def user_list(request):
    if not request.user.is_superuser:
        raise Http404("Não permitido")

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

def login_view(request):
    """Render and process the application login page."""
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.user.is_authenticated:
        return redirect("users:list_users")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        user = authenticate_and_login(request, form)
        if user is not None:
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("users:list_users")

    return render(
        request,
        "users/pages/login.html",
        {
            "form": form,
            "next": next_url,
            "title": "Login",
        },
    )

def logout_view(request):
    """Processa logout via POST e redireciona para a página de login."""
    logout_user(request)
    return redirect("users:login")