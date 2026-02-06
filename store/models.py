from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=10, help_text='Number of items in stock')
    created_date = models.DateTimeField(default=timezone.now, help_text='Date when product was added')
    is_in_stock = models.BooleanField(default=True, help_text='Manually control if product is shown as in stock')
    is_new_arrival = models.BooleanField(default=False, help_text='Manually mark as new arrival')

    def __str__(self):
        return self.name

    def update_stock_status(self):
        """Auto-update is_in_stock based on stock quantity"""
        self.is_in_stock = self.stock > 0
        self.save(update_fields=['is_in_stock'])

    def update_new_arrival_status(self):
        """Auto-update is_new_arrival based on created_date (last 30 days)"""
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        self.is_new_arrival = self.created_date >= thirty_days_ago
        self.save(update_fields=['is_new_arrival'])

    @property
    def average_rating(self):
        """Calculate average rating"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    @property
    def review_count(self):
        """Get count of approved reviews"""
        return self.reviews.filter(is_approved=True).count()

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('fawran', 'Fawran on Delivery'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, help_text='Qatar phone number')
    address = models.CharField(max_length=250, blank=True)
    building = models.CharField(max_length=100, blank=True, null=True, help_text='Building number or name')
    street = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True, help_text='Zone number (Qatar)')
    city = models.CharField(max_length=100, default='Doha')
    postal_code = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id} - {self.first_name} {self.last_name}'

    def get_total_cost(self):
        """Calculate total order cost"""
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """Calculate item cost"""
        return self.price * self.quantity

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True, help_text='Guest name for non-logged-in users')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, help_text='Review must be approved to be visible')

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        name = self.user.username if self.user else self.guest_name
        return f'{name} - {self.product.name} - {self.rating}★'