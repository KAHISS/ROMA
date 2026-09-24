from django import forms
from .models import Sale

INPUT_CLASS = (
    "w-full rounded-md border border-gray-200 bg-white px-3 py-2.5 "
    "text-sm text-gray-900 placeholder:text-gray-400 "
    "focus:border-amber-500 focus:outline-none focus:ring-2 "
    "focus:ring-amber-500/20 transition-colors "
    "dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100 "
    "dark:placeholder:text-neutral-500"
)


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = [
            "client",
            "status",
            "payment_method",
            "discount",
            "freight",
            "cash_received",
        ]
        widgets = {
            "client": forms.TextInput(attrs={"placeholder": "Nome do cliente"}),
            "discount": forms.NumberInput(attrs={"placeholder": "0,00", "step": "0.01", "min": "0"}),
            "freight": forms.NumberInput(attrs={"placeholder": "0,00", "step": "0.01", "min": "0"}),
            "cash_received": forms.NumberInput(attrs={"placeholder": "0,00", "step": "0.01", "min": "0"}),
            "status": forms.Select(),
            "payment_method": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply the common Tailwind class to all fields except the selects
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs["class"] = INPUT_CLASS
            elif isinstance(field.widget, forms.Select):
                # Keep the default select styling – Tailwind styles are applied
                # via the global ``select`` component in the base template.
                pass
