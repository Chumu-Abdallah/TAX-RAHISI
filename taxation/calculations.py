from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

# KWA MUJIBU WA TRA 2024/2025
VAT_RATE = Decimal('0.18')
CORP_RATE = Decimal('0.30')
WHT_RATE = Decimal('0.05')
SDL_RATE = Decimal('0.04')
PRESUMTIVE_RATES = {
    '4000000': Decimal('100000'), # mauzo chini ya 4M
    '7000000': Decimal('150000'),
    '12000000': Decimal('300000'),
}

def quantize_tzs(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_vat(amount_inclusive: Decimal) -> Dict:
    """Hesabu ya VAT Kwa mauzo Ya Tanzania - amount ina jumuishwa VAT"""
    # Formula ya VAT: VAT = Inclusive * 18/118
    vat = amount_inclusive * (Decimal('18') / Decimal('118'))
    net = amount_inclusive - vat
    return {
        'net_amount': quantize_tzs(net),
        'vat_amount': quantize_tzs(vat),
        'gross_amount': quantize_tzs(amount_inclusive)
    }

def calculate_coporate_tax(profit: Decimal) -> Decimal:
    if profit <= 0:
        return Decimal('0.00')
    return quantize_tzs(profit * CORP_RATE)

def calculate_presumtive_tax(annual_turnover: Decimal) -> Decimal:
    """Kwa wafanya Biashara Wadogo Chini Ya 100M Sheria halisi"""
    if annual_turnover <= Decimal('4000000'):
        return PRESUMTIVE_RATES['4000000']
    elif annual_turnover <= Decimal('7000000'):
        return PRESUMTIVE_RATES['7000000']
    elif annual_turnover <= Decimal('12000000'):
        return PRESUMTIVE_RATES['12000000']
    else:
        # Zaidi Ya 12M anapaswa kua VAT
        return Decimal('0.00')

def calculate_paye_and_sdl(basic_salary: Decimal) -> Dict:
    """PAYE - inategemea bands, SDL ni 4% flat"""
    # Simplified Bands TRA 2024 - weka kwenye DB production
    sdl = basic_salary * SDL_RATE 
    # PAYE logic - hapa band ya kwanza 270k ni 0%
    if basic_salary <= Decimal('270000'):
        paye = Decimal('0.00')
    elif basic_salary <= Decimal('520000'):
        paye = (basic_salary - Decimal('270000')) * Decimal('0.09')
    else:
        paye = Decimal('22500') + (basic_salary - Decimal('520000')) * Decimal('0.20')

    return {
        'paye': quantize_tzs(paye),
        'sdl': quantize_tzs(sdl),
        'net_pay': quantize_tzs(basic_salary - paye)
    }