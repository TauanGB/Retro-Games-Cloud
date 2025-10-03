from django.contrib import admin
from .models import Category, Game, Plan, Purchase, Subscription, Entitlement, PaymentSession, GameToken


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'console', 'price', 'is_active', 'created_at']
    list_filter = ['console', 'categories', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'console']
    ordering = ['title']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['categories']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['games']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'amount', 'status', 'purchase_date']
    list_filter = ['status', 'purchase_date']
    search_fields = ['user__username', 'game__title']
    ordering = ['-purchase_date']
    readonly_fields = ['purchase_date', 'idempotency_key']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'current_period_end']
    list_filter = ['status', 'start_date']
    search_fields = ['user__username', 'plan__name']
    ordering = ['-start_date']
    readonly_fields = ['start_date', 'idempotency_key']


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'is_perpetual', 'granted_date']
    list_filter = ['is_perpetual', 'granted_date']
    search_fields = ['user__username', 'game__title']
    ordering = ['-granted_date']
    readonly_fields = ['granted_date']


@admin.register(PaymentSession)
class PaymentSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'plan', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'session_id']
    ordering = ['-created_at']
    readonly_fields = ['session_id', 'created_at']


@admin.register(GameToken)
class GameTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'status', 'created_at', 'last_used_at', 'usage_count']
    list_filter = ['status', 'created_at', 'last_used_at']
    search_fields = ['user__username', 'game__title', 'token']
    ordering = ['-created_at']
    readonly_fields = ['token', 'token_hash', 'created_at', 'last_used_at', 'usage_count']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['user', 'game', 'entitlement']
        return self.readonly_fields