from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile with additional fields."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default='P')
    contact_number = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def picture_url(self):
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        return None


class Item(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('PENDING', 'Pending'),
        ('COLLECTED', 'Collected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='items/%m/%d/%Y/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, blank=True, default='')
    contact_number = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_items')
    claimant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_items')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ITEM_CLAIMED', 'Item Claimed'),
        ('CLAIM_APPROVED', 'Claim Approved'),
        ('CLAIM_REJECTED', 'Claim Rejected'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.item.title} (to {self.recipient.username})"