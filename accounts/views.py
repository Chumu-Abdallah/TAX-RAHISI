from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.utils import timezone
from django.contrib import messages
from .models import User
from .services import authenticate_user_tz
from .permissions import IsAdminOrMkurugenzi, IsActiveVarified, IsMkurugenziOnly
from .forms import RegistrationForm

def normalize_phone_tz(phone):
    """Hii 100% kama ya models.py na login.html"""
    if not phone:
        return None
    p = str(phone).strip().replace(' ', '').replace('-', '')
    if p.startswith('+'):
        p = p[1:]
    if p.startswith('0'):
        p = '255' + p[1:]
    if p.startswith('255'):
        return '+' + p
    if len(p) == 9 and p.isdigit():
        return '+255' + p
    return '+' + p if p else None

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminOrMkurugenzi]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminOrMkurugenzi()]

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        data = request.data if hasattr(request, 'data') else request.POST
        password = data.get('password') or data.get('pawword')
        if not password:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/register.html', {'form': RegistrationForm(), 'error': 'Password inahitajika'})
            return Response({"error": "Password inahitajika"}, status=status.HTTP_400_BAD_REQUEST)

        raw_phone = data.get('phone')
        phone = normalize_phone_tz(raw_phone)
        if not phone:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/register.html', {'form': RegistrationForm(), 'error': 'Namba ya simu inahitajika'})
            return Response({"error": "Namba ya simu inahitajika"}, status=400)

        try:
            user = User.objects.create_user(
                phone=phone,
                username=data.get('username'),
                password=password,
                email=data.get('email'),
                role='OWNER',
                tin_number=data.get('tin_number'),
                nida_number=data.get('nida_number'),
                region=data.get('region'),
                is_active=False,
                is_valified=False
            )
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.success(request, "Akaunti imetumwa kwa Admin kwa uthibitisho. Subiri approval.")
                return redirect('accounts:login')
            return Response(
                {"message": "Akaunti imetumwa kwa Admin kwa uthibitisho. Subiri approval.", "id": str(user.id), "phone": user.phone},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/register.html', {'form': RegistrationForm(), 'error': str(e)})
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PendingUsersView(APIView):
    permission_classes = [IsAdminOrMkurugenzi, IsActiveVarified]

    def get(self, request):
        if request.user.role == 'ADMIN':
            pending = User.objects.filter(is_valified=False, is_active=False, role='OWNER').order_by('-created_at')
        else:
            pending = User.objects.filter(is_valified=False, is_active=False).order_by('-created_at')

        if 'text/html' in request.META.get('HTTP_ACCEPT',''):
            return render(request, 'accounts/pending.html', {'pending_users': pending})

        data = [{"id": str(u.id), "username": u.username, "phone": u.phone, "tin": u.tin_number, "nida": u.nida_number, "region": u.region, "created_at": u.created_at, "role": u.role} for u in pending]
        return Response(data)

class ApproveUserView(APIView):
    permission_classes = [IsAdminOrMkurugenzi, IsActiveVarified]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user.role in ['ADMIN', 'MKURUGENZI'] and request.user.role != 'MKURUGENZI':
                if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                    messages.error(request, "Ni Mkurugenzi pekee anaweza kum-approve Admin/Mkurugenzi")
                    return redirect('/taxpayers/')
                return Response({"error": "Ni Mkurugenzi pekee anaweza kum-approve Admin/Mkurugenzi"}, status=status.HTTP_403_FORBIDDEN)
            
            user.is_active = True
            user.is_valified = True
            user.save(update_fields=['is_active','is_valified'])

            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.success(request, f"{user.username} ame-approve na anaweza ku-login sasa")
                return redirect('/taxpayers/')

            return Response({"message": f"{user.username} ame-approve na anaweza ku-login sasa"})
        except User.DoesNotExist:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.error(request, "User not found")
                return redirect('/taxpayers/')
            return Response({"error": "User not found"}, status=404)

class RejectUserView(APIView):
    permission_classes = [IsAdminOrMkurugenzi, IsActiveVarified]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if str(user.id) == str(request.user.id):
                if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                    messages.error(request, "Huwezi kujifuta mwenyewe")
                    return redirect('/taxpayers/')
                return Response({"error": "Huwezi kujifuta mwenyewe"}, status=403)
            if request.user.role == 'ADMIN' and user.role in ['ADMIN', 'MKURUGENZI']:
                if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                    messages.error(request, "Admin hawezi kumfuta Admin mwenzake au Mkurugenzi.")
                    return redirect('/taxpayers/')
                return Response({"error": "Admin hawezi kumfuta Admin mwenzake au Mkurugenzi. Ni Mkurugenzi pekee."}, status=403)
            if request.user.role == 'MKURUGENZI' and user.role == 'MKURUGENZI' and str(user.id) != str(request.user.id):
                pass
            username = user.username
            user.delete()

            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.success(request, f"Akaunti ya {username} imekataliwa na kufutwa")
                return redirect('/taxpayers/')

            return Response({"message": f"Akaunti ya {username} imekataliwa na kufutwa"})
        except User.DoesNotExist:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.error(request, "User not found")
                return redirect('/taxpayers/')
            return Response({"error": "User not found"}, status=404)

class ApprovedUsersView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVarified]

    def get(self, request):
        current = request.user

        if current.role == 'MKURUGENZI':
            users = User.objects.filter(is_active=True, is_valified=True).order_by('-created_at')
        elif current.role == 'ADMIN':
            users = User.objects.filter(is_active=True, is_valified=True, role='OWNER').order_by('-created_at')
        else:
            users = User.objects.filter(id=current.id)

        if 'text/html' in request.META.get('HTTP_ACCEPT',''):
            return render(request, 'accounts/approved.html', {'approved_users': users})

        data = [{"id": str(u.id), "username": u.username, "phone": u.phone, "tin": u.tin_number, "nida": u.nida_number, "region": u.region, "role": u.role} for u in users]
        return Response(data)

class DeleteApprovedUserView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVarified]

    def post(self, request, user_id):
        try:
            target = User.objects.get(id=user_id)
            current = request.user

            if str(target.id) == str(current.id):
                if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                    messages.error(request, "Huwezi kujifuta mwenyewe")
                    return redirect('/accounts/approved/')
                return Response({"error": "Huwezi kujifuta mwenyewe"}, status=403)

            if current.role == 'OWNER':
                if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                    messages.error(request, "Huna ruhusa ya kumfuta mtu")
                    return redirect('/accounts/approved/')
                return Response({"error": "Owner hawezi kufuta mtu yeyote"}, status=403)

            if current.role == 'ADMIN':
                if target.role in ['ADMIN', 'MKURUGENZI']:
                    if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                        messages.error(request, "Admin hawezi kumfuta Admin au Mkurugenzi")
                        return redirect('/accounts/approved/')
                    return Response({"error": "Admin hawezi kumfuta Admin au Mkurugenzi"}, status=403)

            if current.role == 'MKURUGENZI':
                if target.role == 'MKURUGENZI' and str(target.id) != str(current.id):
                    if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                        messages.error(request, "Huwezi kumfuta Mkurugenzi mwenzako")
                        return redirect('/accounts/approved/')
                    return Response({"error": "Huwezi kumfuta Mkurugenzi mwenzako"}, status=403)

            username = target.username
            target.delete()

            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.success(request, f"{username} amefutwa")
                return redirect('/accounts/approved/')

            return Response({"message": f"{username} amefutwa"})

        except User.DoesNotExist:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.error(request, "User not found")
                return redirect('/accounts/approved/')
            return Response({"error": "User not found"}, status=404)

class CreateAdminView(APIView):
    permission_classes = [IsMkurugenziOnly, IsActiveVarified]

    def post(self, request):
        data = request.data if hasattr(request, 'data') else request.POST
        role = data.get('role', 'ADMIN')
        if role not in ['ADMIN', 'OWNER']:
            return Response({"error": "Mkurugenzi anaweza kutengeneza ADMIN au OWNER tu"}, status=400)
        try:
            phone = normalize_phone_tz(data.get('phone'))
            user = User.objects.create_user(
                phone=phone,
                username=data.get('username'),
                password=data.get('password'),
                email=data.get('email'),
                role=role,
                is_active=True,
                is_valified=True
            )
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.success(request, f"{role} {user.username} ametengenezwa")
                return redirect('/taxpayers/')
            return Response({"message": f"{role} {user.username} ametengenezwa na Mkurugenzi", "id": str(user.id)}, status=201)
        except Exception as e:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                messages.error(request, str(e))
                return redirect('/accounts/create-admin/')
            return Response({"error": str(e)}, status=400)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/login.html')

    def post(self, request):
        data = request.data if hasattr(request, 'data') else request.POST
        raw_phone = data.get('phone') or data.get('username')
        phone = normalize_phone_tz(raw_phone)
        password = data.get('password')

        if not phone or not password:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/login.html', {'error': 'Namba ya simu na password inahitajika'})
            return Response({"error": "Namba ya simu na password inahitajika"}, status=400)

        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')

        user = authenticate_user_tz(phone, password, request_ip=ip)

        if not user:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/login.html', {'error': 'Namba ya simu au password sio sahihi'})
            return Response({"error": "Namba ya simu au password sio sahihi"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role in ['ADMIN', 'MKURUGENZI']:
            if not user.is_active or not user.is_valified:
                user.is_active = True
                user.is_valified = True
                user.is_locked = False
                user.failed_attempts = 0
                user.save(update_fields=['is_active','is_valified','is_locked','failed_attempts'])

        if not user.is_active or not user.is_valified:
            if 'text/html' in request.META.get('HTTP_ACCEPT',''):
                return render(request, 'accounts/login.html', {'error': 'Akaunti yako bado haija-approve na Admin. Subiri.'})
            return Response({"error": "Akaunti yako bado haija-approve na Admin. Subiri."}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)

        if 'text/html' in request.META.get('HTTP_ACCEPT',''):
            return redirect('/dashboard/')

        return Response({"message": "Karibu", "role": user.role, "username": user.username, "phone": user.phone}, status=status.HTTP_200_OK)