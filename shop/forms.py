from django import forms
from .models import Product, ReviewRating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['review', 'rating']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        localized_fields = ['price']