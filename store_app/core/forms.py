from django import forms
from store_app.api.models import Cart
from store_app.tools.helpers import *

class HtmxForm(forms.Form):
    name=forms.CharField()
    age=forms.IntegerField()

    def clean_name(self):
        if self.cleaned_data.get('name').startswith('a'):
            raise forms.ValidationError('Name cannot start with a')
        

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "input input-bordered", "placeholder": "Email", "required": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered", "placeholder": "Password", "required": True}),
    )

class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "input input-bordered", "placeholder": "Email", "required": True}),
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "input input-bordered", "placeholder": "Username", "required": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered", "placeholder": "Password", "required": True}),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered", "placeholder": "Password", "required": True}),
    )
    phone = forms.IntegerField(
        label="Phone",
        widget=forms.NumberInput(attrs={"class": "input input-bordered", "placeholder": "Phone", "required": True}),
    )
    image = forms.ImageField(
        label="Account Photo",
        widget=forms.FileInput(attrs={"id": "image-input", "class": "file-input file-input-bordered file-input-success w-full max-w-xs", "placeholder": "Account Photo", "required": True}),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            self.add_error('password', 'Passwords do not match.')

        return cleaned_data
    
    def clean_image(self):
        image = self.files.get('image')

        if image is not None:
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.add_error('image', 'Invalid file format. Please upload a valid image.')
            if image.size > 5 * 1024 * 1024:  # 5 MB
                self.add_error('image', 'File size exceeds the allowed limit (5 MB)')

        return image
    
class ReviewForm(forms.Form):
    comment = forms.CharField(
        label="Comment",
        widget=forms.Textarea(attrs={"class": "textarea textarea-primary my-5 w-full", "placeholder": "Enter your game review", "rows": "2", "required": True}),
    )
    # rating = forms.IntegerField(
    #     min_value=1,
    #     max_value=5, 
    #     widget=forms.RadioSelect(
    #         choices=[(1, ''), (2, ''), (3, ''), (4, ''), (5, '')], 
    #         attrs={"class": "mask mask-star-2 bg-teal-500 review-star-rating", "name": "rating"}
    #         )
    # )
class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(
            attrs={
                "id": "quantity",
                "class": "input input-bordered input-info w-full max-w-xs",
                "placeholder": "Choose quantity",
                "required": True,
                "min": 1,  # Set the minimum value
                # "max": 10,  # Set the maximum value dynamically from views
            }
        ),
    )
class DeleteCartForm(forms.Form):
    cart_id = forms.UUIDField()

    def delete_cart(self):
        try:
            logger.info(f"Deleting cart with id: {self.cleaned_data['cart_id']}")
            Cart.objects.get(id=str(self.cleaned_data['cart_id'])).delete()
        except Cart.DoesNotExist:
            logger.error(f"Cart with id: {self.cleaned_data['cart_id']} does not exist")