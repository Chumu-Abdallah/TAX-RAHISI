import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    MKURUGENZI = 'MKURUGENZI', 'Mkurugenzi'
    AFISA_KODI = 'AFISA_KODI', 'Afisa kodi'
    MHASIBU = 'MHASIBU', 'Mhasibu'
    BUSINESS_OWNER = 'OWNER', 'Mmiliki wa Biashara'

class CustomsUserManager(BaseUserManager):
    def _normalize_phone(self, phone):
        """Normalizes 0xxx -> +255xxx, 255xxx -> +255xxx, 7xxxxxxxx -> +255xxx, +255xxx -> +255xxx"""
        if not phone:
            return phone
        p = str(phone).strip().replace(' ', '').replace('-', '')
        if p.startswith('+'):
            p = p[1:]
        if p.startswith('0'):
            return '+255' + p[1:]
        if p.startswith('255'):
            return '+' + p
        if len(p) == 9 and p.isdigit():  # 714975460
            return '+255' + p
        return '+' + p

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Namba ya simu Inahitajika')
        
        phone = self._normalize_phone(phone)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_valified', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser lazima awe is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser lazima awe is_superuser=True')

        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(unique=True, null=True, blank=True, default=None, db_index=True)

    # Uboreshaji: Inaruhusu +255, 255, 0, na 9 digits - zote zitanormalize kwenda +255
    phone_validator = RegexValidator(
        regex=r'^(\+?255|0)?\d{9}$', 
        message='Namba Iwe +255XXXXXXXXX, 255XXXXXXXXX, 07XXXXXXXXX au 7XXXXXXXXX'
    )
    phone = models.CharField(max_length=13, unique=True, validators=[phone_validator], db_index=True)

    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.BUSINESS_OWNER, db_index=True)

    tin_number = models.CharField(
        max_length=20, blank=True, null=True, 
        verbose_name="TIN",
        validators=[RegexValidator(r'^\d{9,10}$', 'TIN lazima iwe tarakimu 9-10')],
        db_index=True
    )
    nida_number = models.CharField(
        max_length=20, blank=True, null=True, 
        verbose_name="NIDA",
        validators=[RegexValidator(r'^\d{20}$', 'NIDA lazima iwe tarakimu 20')],
    )
    region = models.CharField(max_length=50, blank=True, db_index=True)

    is_active = models.BooleanField(default=True, help_text="Account imezimwa au la")
    is_staff = models.BooleanField(default=False)
    is_valified = models.BooleanField(default=False, verbose_name="Amehakikiwa")

    failed_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    last_failed_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomsUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Mtumiaji"
        verbose_name_plural = "Watumiaji"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.username} - {self.phone}"

    @property
    def is_verified(self):
        return self.is_valified

    @property
    def is_account_locked(self):
        # FIX: kama last_failed_at ni None, account haiko locked
        if not self.is_locked:
            return False
        if not self.last_failed_at:
            return False
        # FIX: kama dakika 30 zimepita, fungua na futa last_failed_at pia
        if timezone.now() > self.last_failed_at + timedelta(minutes=30):
            self.is_locked = False
            self.failed_attempts = 0
            self.last_failed_at = None
            try:
                self.save(update_fields=['is_locked', 'failed_attempts', 'last_failed_at'])
            except:
                try:
                    self.save()
                except:
                    pass
            return False
        return True

    def can_manage_users(self):
        return self.role in [UserRole.ADMIN, UserRole.MKURUGENZI]

    def can_view_all_businesses(self):
        return self.role in [UserRole.ADMIN, UserRole.MKURUGENZI, UserRole.AFISA_KODI, UserRole.MHASIBU]

    def is_business_owner_only(self):
        return self.role == UserRole.BUSINESS_OWNER

    def increment_failed_attempt(self):
        self.failed_attempts += 1
        self.last_failed_at = timezone.now()
        if self.failed_attempts >= 5:
            self.is_locked = True
        try:
            self.save(update_fields=['failed_attempts', 'last_failed_at', 'is_locked'])
        except:
            self.save()

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.is_locked = False
        self.last_failed_at = None
        try:
            self.save(update_fields=['failed_attempts', 'is_locked', 'last_failed_at'])
        except:
            self.save()