from django.core.exceptions import ValidationEroor
from decimal import Decimal

def validate_tin(value):
    if not value.isdigit() or len(value) not in [9, 10]:
        raise ValidationEroor("Tin ya TRA lazima Iwe Tarakimu 9 au 10")\


def validate_turnover(value):
    if value < 0:
        raise ValidationEroor("Mauzo hayawezi kua Chin ya 0.")
    if value > Decimal('100000000000'): # 100B
        raise ValidationEroor("auzo makubwa sana, Hakikish")       