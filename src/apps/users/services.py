from django.contrib.auth import get_user_model

from apps.users.filters import UserFilter
from utils.pagination import make_pagination


User = get_user_model()


def get_user_list_context(request, per_page=10):
    """Return filtered and paginated users for the user management page."""
    queryset = User.objects.all().order_by("-date_joined")

    user_filter = UserFilter(request.GET, queryset=queryset)
    filtered_users = user_filter.qs

    users, pagination_range = make_pagination(
        request, filtered_users, per_page
    )

    get_copy = request.GET.copy()
    if "page" in get_copy:
        del get_copy["page"]
    additional_url_query = "&" + get_copy.urlencode() if get_copy else ""

    return {
        "filter": user_filter,
        "pagination_range": pagination_range,
        "objects": users,
        "users": users,
        "additional_url_query": additional_url_query,
    }


def create_user(form):
    """Validate and persist a user submitted through UserForm."""
    if not form.is_valid():
        return None

    return form.save()