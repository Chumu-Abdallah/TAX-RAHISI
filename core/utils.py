# core/utils.py
import locale
from decimal import Decimal

def format_tzs(amount: Decimal) -> str:
    """Rudish kama TZS 1,234,500"""
    try:
        return f"TZS {amount:,.2f}"
    except:
        return f"TZS {amount}"

def generate_control_number():
    """kama ya TRA GePG - 12 digits"""
    import random, datetime
    prefix = datetime.datetime.now().strftime('%y%m')
    suffix = random.randint(10**8, 10**9-1)
    return f"{prefix}{suffix}"    

def is_valid_finacial_year(year: int) -> bool:
    return 2020 <= year # <= 2050