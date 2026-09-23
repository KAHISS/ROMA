from django import forms

from apps.inventory.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "barcode",
            "description",
            "brand",
            "cust",
            "price",
            "quantity",
            "min_quantity",
        ]
        widgets = {
            "barcode": forms.TextInput(
                attrs={"placeholder": "Ex.: 7891234567890"}
            ),
            "description": forms.TextInput(
                attrs={"placeholder": "Ex.: Cigarro, isqueiro ou bebida"}
            ),
            "brand": forms.TextInput(
                attrs={"placeholder": "Ex.: Marca do produto"}
            ),
            "cust": forms.NumberInput(
                attrs={"placeholder": "0,00", "step": "0.01", "min": "0"}
            ),
            "price": forms.NumberInput(
                attrs={"placeholder": "0,00", "step": "0.01", "min": "0"}
            ),
            "quantity": forms.NumberInput(
                attrs={"placeholder": "0", "min": "0"}
            ),
            "min_quantity": forms.NumberInput(
                attrs={"placeholder": "5", "min": "0"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        input_class = (
            "w-full rounded-md border border-gray-200 bg-white px-3 py-2.5 "
            "text-sm text-gray-900 placeholder:text-gray-400 "
            "focus:border-amber-500 focus:outline-none focus:ring-2 "
            "focus:ring-amber-500/20 transition-colors "
            "dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100 "
            "dark:placeholder:text-neutral-500"
        )

        for field in self.fields.values():
            field.widget.attrs["class"] = input_class