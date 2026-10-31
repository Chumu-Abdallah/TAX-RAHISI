from django import forms
from django.core.validators import RegexValidator
from .models import User, UserRole

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Weka nenosiri'}),
        min_length=8,
        help_text="Nenosiri angalau herufi 8"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Rudia nenosiri'})
    )

    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'role', 'tin_number', 'nida_number', 'region']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2557...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'tin_number': forms.TextInput(attrs={'class': 'form-control'}),
            'nida_number': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return User.objects._normalize_phone(phone) if hasattr(User.objects, '_normalize_phone') else phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Nenosiri hazifanani")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user