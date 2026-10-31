from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Taxpayer
from .services import TaxpayerService
from .forms import TaxpayerRegistrationForm
from accounts.permissions import IsActiveVarified, IsAdminOrMkurugenzi

class TaxpayerCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        form = TaxpayerRegistrationForm()
        return render(request, 'taxpayers/register.html', {'form': form})

    def post(self, request):
        # Kama ni browser (HTML) - tumia form validation
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            form = TaxpayerRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    # Unaweza ku-save moja kwa moja au kupitia service
                    taxpayer = form.save(commit=False)
                    # kama service yako inahitaji user
                    taxpayer = TaxpayerService.register_taxpayer(request.user, form.cleaned_data)
                    return redirect('/taxpayers/')
                except Exception as e:
                    return render(request, 'taxpayers/register.html', {'form': form, 'error': str(e)})
            else:
                return render(request, 'taxpayers/register.html', {'form': form})

        # Kama ni API (JSON) - endelea na logic yako ya mwanzo
        try:
            taxpayer = TaxpayerService.register_taxpayer(request.user, request.data)
            return Response({
                "message": "Umesajiliwa, Subiri Uthibitisho",
                "tin": taxpayer.tin_number,
                "id": str(taxpayer.id)
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class TaxpayerDetailView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVarified]

    def get(self, request, pk=None):
        taxpayer_obj = None
        if pk and request.user.role in ['ADMIN', 'MKURUGENZI']:
            taxpayer_obj = get_object_or_404(Taxpayer, pk=pk)
        else:
            try:
                taxpayer_obj = request.user.taxpayer_profile
            except Taxpayer.DoesNotExist:
                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    return render(request, 'taxpayers/detail.html', {'taxpayer': None, 'error': 'Huna profile'})
                return Response({"error": "Huna profile ya mlipa kodi."}, status=404)

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'taxpayers/detail.html', {'taxpayer': taxpayer_obj, 't': taxpayer_obj})

        data = {
            "id": str(taxpayer_obj.id),
            "full_name": taxpayer_obj.full_name,
            "tin": taxpayer_obj.tin_number,
            "type": taxpayer_obj.get_taxpayer_type_display(),
            "region": taxpayer_obj.region,
            "status": taxpayer_obj.verification_status,
            "is_vat": taxpayer_obj.is_vat_registered
        }
        return Response(data)

class TaxpayerVerifyView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrMkurugenzi]

    def post(self, request, pk):
        taxpayer = TaxpayerService.verify_taxpayer(pk, request.user)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return redirect(f'/taxpayers/{pk}/')
        return Response({"message": f"{taxpayer.tin_number} imethibitishwa"})

class TaxpayerRejectView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrMkurugenzi]

    def post(self, request, pk):
        taxpayer = get_object_or_404(Taxpayer, pk=pk)
        taxpayer.verification_status = 'REJECTED'
        taxpayer.save()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return redirect('/taxpayers/')
        return Response({"message": f"{taxpayer.tin_number} imekataliwa"})

class TaxpayerDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrMkurugenzi]

    def post(self, request, pk):
        taxpayer = get_object_or_404(Taxpayer, pk=pk)
        taxpayer.delete()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return redirect('/taxpayers/')
        return Response({"message": "imefutwa"})

class TaxpayerListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrMkurugenzi]

    def get(self, request, *args, **kwargs):
        taxpayers = Taxpayer.objects.all().order_by('-created_at')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        pending_users = User.objects.filter(
            is_active=False, 
            role__in=['OWNER', 'MTAALAMU_KODI']
        ).order_by('-created_at')

        pending_count = taxpayers.filter(verification_status='PENDING').count() + pending_users.count()

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'taxpayers/list.html', {
                'taxpayers': taxpayers,
                'pending_users': pending_users,
                'pending_count': pending_count
            })

        data = [
            {
                "id": str(t.id),
                "full_name": t.full_name,
                "tin": t.tin_number,
                "type": t.get_taxpayer_type_display(),
                "region": t.region,
                "status": t.verification_status,
                "is_vat": t.is_vat_registered
            }
            for t in taxpayers
        ]
        return Response(data)