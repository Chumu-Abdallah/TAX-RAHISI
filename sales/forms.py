from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'business',
            'invoice_no',
            'customer_name',
            'customer_tin',
            'sale_date',
            'amount_excl_vat',
            'vat_amount',
            'amount_incl_vat',
            'has_efd_receipt',
            'efd_receipt_no'
        ]
        widgets = {
            'business': forms.Select(attrs={'class': 'form-select'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_tin': forms.TextInput(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount_excl_vat': forms.NumberInput(attrs={'class': 'form-control'}),
            'vat_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'amount_incl_vat': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_efd_receipt': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'efd_receipt_no': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Auto calc kama user hajaweka incl
        excl = cleaned.get('amount_excl_vat')
        vat = cleaned.get('vat_amount')
        incl = cleaned.get('amount_incl_vat')
        
        if excl is not None and vat is not None and not incl:
            cleaned['amount_incl_vat'] = excl + vat
            
        return cleaned