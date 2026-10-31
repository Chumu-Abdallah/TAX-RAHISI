from django import forms
from .models import Taxpayer
from core.validators import validate_tin, validate_nida

class TaxpayerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Taxpayer
        fields = ['tin_number', 'nida_number', 'taxpayer_type', 'first_name', 'middle_name', 'last_name', 'business_name', 'region', 'district', 'ward']

    def clean_tin_number(self):
        tin = self.cleaned_data['tin_number']
        validate_tin(tin)
        return tin

    def clean_nida_number(self):
        nida = self.cleaned_data['nida_number']
        validate_nida(nida)
        return nida

    def clean(self):
        cleaned = super().clean()
        t_type = cleaned.get('taxpayer_type')
        b_name = cleaned.get('business_name')
        if t_type in ['LTD', 'SOLE'] and not b_name:
            raise forms.ValidationError("Jina la biashara Linahitajika kwa Kampuni / Biashara Ndogo.")
        return cleaned