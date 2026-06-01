from django.contrib import admin
from .models import Item, Notification

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor', 'status', 'claimant', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'donor__username', 'claimant__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Item Details', {
            'fields': ('title', 'description', 'image')
        }),
        ('Location & Contact', {
            'fields': ('latitude', 'longitude', 'address', 'contact_number')
        }),
        ('Status & Ownership', {
            'fields': ('status', 'donor', 'claimant')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'item', 'actor', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'actor__username', 'item__title']
    readonly_fields = ['created_at']
