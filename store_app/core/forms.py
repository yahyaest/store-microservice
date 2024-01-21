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