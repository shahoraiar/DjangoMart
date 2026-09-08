from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'address_line1', 'address_line2', 'city', 'country', 'state', 'order_note',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional fields (UI allows empty)
        self.fields['address_line2'].required = False
        self.fields['order_note'].required = False
