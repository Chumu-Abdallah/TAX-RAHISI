from django import forms
from .models import Expense
from decimal import Decimal

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'title', 'description', 'amount', 'vat_amount', 'receipt_number', 'supplier_tin', 'expense_date', 'receipt_file']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'vat_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Gharama Lazima iwe Zaidi Ya 0")
        if amount > Decimal('1000000000'):
            raise forms.ValidationError("Kiasi Kikubwa mno, hakikisha")
        return amount

    def clean(self):
        cleaned = super().clean()
        cat = cleaned.get('category')
        tin = cleaned.get('supplier_tin')
        vat = cleaned.get('vat_amount') or Decimal('0')
        if vat > 0 and not tin:
            raise forms.ValidationError("Ukiweka VAT lazima Uweke TIN ya Muuzaji Kwaajili ya TRA")
        return cleaned