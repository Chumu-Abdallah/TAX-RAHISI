from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Expense
from .services import ExpenseService
from accounts.permissions import IsActiveVarified
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class ExpenseListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsActiveVarified]
    serializer_class = ExpenseSerializer
    def get_queryset(self):
        user = self.request.user
        try:
            return Expense.objects.filter(taxpayer=user.taxpayer_profile).select_related('business').order_by('-expense_date')
        except:
            return Expense.objects.none()
    def perform_create(self, request):
        business_id = request.data.get('business_id')
        if not business_id:
            raise ValueError("business_id inahitajika")
        from businesses.models import Business
        business = Business.objects.get(id=business_id, taxpayer=request.user.taxpayer_profile)
        return ExpenseService.create_expense(
            business=business,
            taxpayer=request.user.taxpayer_profile,
            user=request.user,
            validate_data={
                'category': request.data['category'],
                'title': request.data['title'],
                'description': request.data.get('description', ''),
                'amount': request.data['amount'],
                'vat_amount': request.data.get('vat_amount', 0),
                'receipt_number': request.data.get('receipt_number', ''),
                'supplier_tin': request.data.get('supplier_tin', ''),
                'expense_date': request.data['expense_date'],
            }
        )
    def post(self, request, *args, **kwargs):
        try:
            expense = self.perform_create(request)
            return Response({"message": "Gharama Imehifadhiwa", "id": str(expense.id)}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVarified]
    def get(self, request):
        year = request.query_params.get('year', 2025)
        month = request.query_params.get('month', 10)
        business_id = request.query_params.get('business_id')
        if not business_id:
            return Response({"error": "business_id inahitajika"}, status=400)
        try:
            from businesses.models import Business
            business = Business.objects.get(id=business_id, taxpayer=request.user.taxpayer_profile)
            summary = ExpenseService.get_monthly_summary(business, int(year), int(month))
            return Response(summary)
        except Business.DoesNotExist:
            return Response({"error": "Biashara haipo"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# ===== HTML PAGES - Bila base.html dependency =====
@login_required
def expense_html_page(request):
    try:
        expenses = Expense.objects.filter(taxpayer=request.user.taxpayer_profile).select_related('business').order_by('-expense_date')
    except:
        expenses = []
    # Jaribu template yako, kama haipo leta HTML rahisi
    try:
        return render(request, 'expenses/list.html', {'expenses': expenses})
    except:
        from django.http import HttpResponse
        html = f"<h1>Gharama Zangu</h1><p>Idadi: {len(expenses)}</p><ul>"
        for e in expenses:
            html += f"<li>{e.title} - {e.total_amount} TZS</li>"
        html += "</ul><a href='/expenses/create/'>Ongeza Gharama</a>"
        return HttpResponse(html)

@login_required
def expense_create_page(request):
    from businesses.models import Business
    try:
        businesses = Business.objects.filter(taxpayer=request.user.taxpayer_profile)
    except:
        businesses = []
    return render(request, 'expenses/form.html', {'businesses': businesses})

@login_required
def expense_detail_page(request, pk):
    try:
        expense = Expense.objects.get(id=pk, taxpayer=request.user.taxpayer_profile)
        return render(request, 'expenses/detail.html', {'expense': expense})
    except Expense.DoesNotExist:
        from django.http import HttpResponse
        return HttpResponse("Gharama haipo", status=404)