from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from.calculations import calculate_vat, calculate_presumtive_tax
from decimal import Decimal

class TaxCalculatorView(APIView):
    permission_calsses = [IsAuthenticated]

    def post(self, request):
        amount = Decimal(request.data.get('amount', '0'))
        tax_type = request.data.get('tax_type', 'VAT')

        if tax_type == 'VAT':
            result = calculate_vat(amount)
        elif tax_type == 'PRES':
            result = {'tax': calculate_presumtive_tax(amount)}
        else:
            result = {}
        return Response(result)          
