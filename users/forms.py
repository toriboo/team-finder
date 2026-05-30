from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate  # <-- добавьте эту строку
from django.core.exceptions import ValidationError
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаляем стандартное поле username
        if "username" in self.fields:
            del self.fields["username"]

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email is not None and password:
            # Теперь authenticate импортирован
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise ValidationError(
                "Пользователь с таким номером телефона уже существует"
            )
        return phone

    def clean_github_url(self):
        url = self.cleaned_data["github_url"]
        if url and "github.com" not in url:
            raise ValidationError("Ссылка должна вести на GitHub")
        return url


class ChangePasswordForm(PasswordChangeForm):
    pass
