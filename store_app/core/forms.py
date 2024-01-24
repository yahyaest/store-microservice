from django import forms

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