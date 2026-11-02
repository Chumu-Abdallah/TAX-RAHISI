# core/validators.py
import re
from django.core.exceptions import ValidationError

def validate_tin(value):
    """TIN ya TRA: Namba 9 au 10 digits, inakubali na 123-456-789"""
    raw = str(value).strip()
    # Ondoa dash kwa ajili ya check
    digits = raw.replace('-', '')
    # Model yako inataka 9 au 10 digits
    if not re.match(r'^\d{9,10}$', digits):
        raise ValidationError('TIN si sahihi. Inatakiwa 123-456-789 au 123456789 (9 au 10 digits)')
    # Kama ni 123-456-789 (9 digits) ni sawa, kama ni 123456789 pia sawa
    return digits

def validate_nida(value):
    """NIDA ya Tanzania: 20 digits"""
    raw = str(value).strip().replace('-', '').replace(' ', '')
    if not re.match(r'^\d{20}$', raw):
        raise ValidationError('NIDA namba Inatakiwa Iwe Tarakimu 20 Sahihi')
    return raw

def validate_tz_phone(value):
    """+255 6xx/7xx au 0xx - Inafanya kazi kwa +255712345678, 0712345678, 0712 345 678"""
    # FIX: uliandika replace(' ', ' ') badala ya replace(' ', '')
    cleaned = str(value).strip().replace(' ', '').replace('-', '')
    pattern = r'^(?:\+255|0)[67]\d{8}$'
    if not re.match(pattern, cleaned):
        raise ValidationError('Namba ya simu haiendani na namba za simu za Tanzania. Mf: 0712345678 au +255712345678')
    return cleaned

def validate_tzs_amount(value):
    """Hii ndio sahihi"""
    try:
        v = float(value)
    except:
        raise ValidationError('Kiasi si namba sahihi')
    if v < 0:
        raise ValidationError('Kiasi Halisi hakiwezi kuwa chini ya 0')
    if v > 100_000_000_000:  # 100B
        raise ValidationError('Kiasi Kikubwa mno! Zaidi ya TZS 100B')
    return v

# Alias ili code yako ya zamani isiharibike - uliita validate_tzs_amoun (bila t)
def validate_tzs_amoun(value):
    """Backward compatibility - usifute, code zako za zamani zinaiita"""
    return validate_tzs_amount(value)