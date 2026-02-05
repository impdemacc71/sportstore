from django import forms
from .models import Order, Review

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class OrderCreateForm(forms.ModelForm):
    """Checkout form with Qatar-specific address fields"""
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+974 XXXX XXXX'}),
        help_text='Qatar phone number (e.g., +974 4444 5555)'
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'building', 'street', 'zone', 'city', 'postal_code',
            'payment_method'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Area or landmark'}),
            'building': forms.TextInput(attrs={'placeholder': 'Building number or name'}),
            'street': forms.TextInput(attrs={'placeholder': 'Street name'}),
            'zone': forms.TextInput(attrs={'placeholder': 'Zone number (e.g., Zone 51)'}),
            'city': forms.TextInput(attrs={'value': 'Doha'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'ZIP code (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget = forms.RadioSelect(choices=Order.PAYMENT_CHOICES)
        self.fields['payment_method'].initial = 'cod'
        self.fields['payment_method'].label = 'Payment Method'

class ReviewForm(forms.ModelForm):
    """Product review form with star rating"""
    RATING_CHOICES = [(i, f'{i} ★') for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label='Your Rating'
    )

    guest_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your name (optional if logged in)'
        }),
        label='Your Name'
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].label = 'Your Review'