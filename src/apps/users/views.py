import environ

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.users.forms import UserForm
from apps.users.services import create_user, get_user_list_context

env = environ.Env()

PER_PAGE = env.int("PER_PAGE", default=12)


@login_required
def user_list(request):
    form = UserForm()

    if request.method == "POST":
        form = UserForm(request.POST)
        user = create_user(form)

        if user is not None:
            return redirect("users:list_users")

    context = get_user_list_context(request, PER_PAGE)
    context.update({
        "form": form,
        "title": "Usuários",
        "page": "users",
    })

    return render(request, "users/pages/users.html", context)
