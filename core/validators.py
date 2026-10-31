# core/validator
import re
from django.core.exceptions import ValidationError

def validate_tin(value):
    """TIN ya TRA: Namba 9 zenye format 123-456-789"""
    pattern = r'^\d{3}-\d{3}-\d{3}$|^\d{9}$'
    if not re.match(pattern, str(value)):
        raise ValidationError('TIN si sahihi. Inatakiwa 123-456-789 au 123456789')

def validate_nida(value):
        """NIDA ya Tanzania: 20 digits"""
        if not re.match(r'^\d{20}$', str(value)):
            raise ValidationError('NIDA namba Inatakiwa Iwe Tarakimu 20 Sahihi')

def validate_tz_phone(value):
    """+255 6xx/7xx au 0xx"""
    pattern = r'^(?:\+255|0)[67]\d{8}$'
    if not re.match(pattern, str(value).replace(' ', ' ')):
        raise ValidationError('Namba ya simu haiendani na namba zasimu za Tanzania.')

def validate_tzs_amoun(value):
    if value < 0:
        raise ValidationError('Kiasi Halisi hakiwezi kua chini ya 0')
    if value > 100_000_000_000: #100B
        raise ValidationError('Kiasi Kikubwa mno!')    