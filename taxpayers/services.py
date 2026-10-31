from django.utils import timezone
from django.db import transaction 
from .models import Taxpayer, VerificationStatus
import logging

logger = logging.getLogger(__name__)

class TaxpayerService:
    @staticmethod
    @transaction.atomic
    def register_taxpayer(user, validate_data):
        """Tengeneza Taxpayer na user alie login - production Safe"""
        if hasattr(user, 'taxpayer_profile'):
            raise ValueError("Mtumiaji Huyu Tayari Ana profile(wasifu) ya Mlipa kodi")

        taxpayer = Taxpayer.objects.create(
            user=user,
            **validate_data,
            verification_status = VerificationStatus.PENDING
        )
        logger.info(f"Taxpayer {taxpayer.tin_number} Registered by {user.phone}")
        return taxpayer

    @staticmethod
    @transaction.atomic
    def verify_taxpayer(taxpayer_id, verified_by_user):
        """Hii inaitwa na Afisakdi Au admini Baada yakucheki kNIDA/TRA API"""
        taxpayer = Taxpayer.objects.select_for_update().get(id=taxpayer_id)
        taxpayer.verification_status = VerificationStatus.VERIFIED
        taxpayer.verified_at = timezone.now()
        taxpayer.save()

        # Update user - is_verified ni property, kwa hiyo tuna-activate tu user
        user = taxpayer.user
        user.is_active = True
        user.save(update_fields=['is_active'])
        return taxpayer

    @staticmethod
    def get_taxpayer_dashboard_status(taxpayer):
        """Kwa dashboard.html"""
        from businesses.models import Business
        businesses_count = Business.objects.filter(taxpayer=taxpayer).count()
        return{
            'businesses': businesses_count,
            'is_vat': taxpayer.is_vat_registered,
            'status': taxpayer.verification_status,
        }