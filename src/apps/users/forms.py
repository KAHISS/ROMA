from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm


User = get_user_model()

INPUT_CLASS = (
    "w-full rounded-md border border-gray-200 bg-white px-3 py-2.5 "
    "text-sm text-gray-900 placeholder:text-gray-400 "
    "focus:border-amber-500 focus:outline-none focus:ring-2 "
    "focus:ring-amber-500/20 transition-colors "
    "dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100 "
    "dark:placeholder:text-neutral-500"
)


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "is_superuser",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Ex.: João"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Ex.: Silva"}),
            "username": forms.TextInput(attrs={"placeholder": "Ex.: joao.silva"}),
            "email": forms.EmailInput(attrs={"placeholder": "Ex.: joao@empresa.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_superuser"].label = "Administrador"
        self.fields["is_superuser"].help_text = (
            "Concede acesso total à administração do sistema."
        )
        self.fields["is_superuser"].widget.attrs["class"] = (
            "h-4 w-4 rounded border-gray-300 text-amber-500 "
            "focus:ring-amber-500/20 dark:border-neutral-700 "
            "dark:bg-neutral-900"
        )

        for field_name, field in self.fields.items():
            if field_name != "is_superuser":
                field.widget.attrs["class"] = INPUT_CLASS

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = user.is_superuser

        if commit:
            user.save()
            self.save_m2m()

        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "is_superuser"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Ex.: João"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Ex.: Silva"}),
            "username": forms.TextInput(attrs={"placeholder": "Ex.: joao.silva"}),
            "email": forms.EmailInput(attrs={"placeholder": "Ex.: joao@empresa.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS


class UserPasswordForm(SetPasswordForm):
    """Form for an administrator to define a new password for a user."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": INPUT_CLASS,
                "placeholder": "Digite a nova senha",
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": INPUT_CLASS,
                "placeholder": "Confirme a nova senha",
            }
        )
