from django import forms
from.models import Business

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'taxpayer', 'business_name', 'trade_name',
            'brela_reg_no', 'tin', 'business_type',
            'region', 'district', 'ward',
            'annual_turnover', 'is_vat_registered', 'vat_number'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'brela_reg_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456'}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123-456-789'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_turnover': forms.NumberInput(attrs={'class': 'form-control'}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_brela_reg_no(self):
        reg_no = self.cleaned_data['brela_reg-no'].strip().upper()
        if len(reg_no) < 5:
            raise forms.ValidationError("BRELA No si sahihi.")
        return reg_no

    def clean(self):
        cleaned = super().clean()
        is_vat = cleaned.get('is_vat_registered')
        vat_no = cleaned.get('vat_number')
        turnover = cleaned.get('annual_turnover') or 0

        if is_vat and not vat_no:
            self.add_error('vat_number', 'VAT Number inahitajika ukiwa ume-register VAT.')
            if turnover >= Business.VAT_THRESHOLD and not is_vat:
                # hii sio Error, ni warning kwa view
                cleaned['requires_vat_notice'] = True
            return cleaned


# form ofauti kwa update - taxpayer isi-editable
class BusinessUpdateForm(BusinessForm):
    class Meta(BusinessForm.Meta):
        exclude = ['taxpayer']        