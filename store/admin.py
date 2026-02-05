from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_date', 'is_in_stock', 'is_new_arrival']
    list_filter = ['category', 'created_date', 'stock', 'is_in_stock', 'is_new_arrival']
    search_fields = ['name', 'description']
    list_editable = ['stock', 'price', 'is_in_stock', 'is_new_arrival']
    readonly_fields = ['created_date', 'average_rating', 'review_count']
    actions = ['update_stock_status', 'update_new_arrival_status', 'calculate_all_statuses']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_in_stock')
        }),
        ('Product Status', {
            'fields': ('is_new_arrival',)
        }),
        ('Statistics', {
            'fields': ('created_date', 'average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )

    def update_stock_status(self, request, queryset):
        """Auto-update is_in_stock based on stock quantity"""
        updated = 0
        for product in queryset:
            product.update_stock_status()
            updated += 1
        self.message_user(request, f'{updated} products stock status updated based on quantity.')
    update_stock_status.short_description = 'Auto-calculate stock status'

    def update_new_arrival_status(self, request, queryset):
        """Auto-update is_new_arrival based on created_date (last 30 days)"""
        updated = 0
        for product in queryset:
            product.update_new_arrival_status()
            updated += 1
        self.message_user(request, f'{updated} products new arrival status updated based on date.')
    update_new_arrival_status.short_description = 'Auto-calculate new arrival status'

    def calculate_all_statuses(self, request, queryset):
        """Auto-calculate both stock and new arrival status"""
        updated = 0
        for product in queryset:
            product.update_stock_status()
            product.update_new_arrival_status()
            updated += 1
        self.message_user(request, f'{updated} products status updated (stock & new arrival).')
    calculate_all_statuses.short_description = 'Auto-calculate all statuses'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'payment_method', 'paid', 'created', 'get_total_cost']
    list_filter = ['paid', 'payment_method', 'created']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created', 'updated', 'get_total_cost']
    fieldsets = (
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address (Qatar)', {
            'fields': ('address', 'building', 'street', 'zone', 'city', 'postal_code')
        }),
        ('Order Information', {
            'fields': ('payment_method', 'paid', 'created', 'updated', 'get_total_cost')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['product']
    search_fields = ['product__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_reviewer_name', 'rating', 'is_approved', 'created_date']
    list_filter = ['is_approved', 'rating', 'created_date']
    search_fields = ['product__name', 'user__username', 'guest_name', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_date']
    actions = ['approve_reviews']

    def get_reviewer_name(self, obj):
        return obj.guest_name or (obj.user.username if obj.user else 'Guest')
    get_reviewer_name.short_description = 'Reviewer'

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
