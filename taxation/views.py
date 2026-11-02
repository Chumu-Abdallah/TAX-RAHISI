from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .calculations import calculate_vat, calculate_presumtive_tax
from decimal import Decimal, InvalidOperation

class TaxCalculatorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, ValueError, TypeError):
            return Response({"error": "amount lazima iwe namba"}, status=400)

        tax_type = request.data.get('tax_type', 'VAT')

        if tax_type == 'VAT':
            result = calculate_vat(amount)
        elif tax_type == 'PRES':
            result = {'tax': calculate_presumtive_tax(amount)}
        else:
            result = {}
            return Response({"error": f"tax_type '{tax_type}' haijulikani"}, status=400)
        
        return Response(result)