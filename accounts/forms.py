from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.models import BestSet, Exercise


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Required field. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Register", css_class="btn-primary"))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists")
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class BestSetForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.all(),
        label="Exercise",
        required=True,
    )

    class Meta:
        model = BestSet
        fields = ["exercise", "weight", "reps"]
        labels = {
            "weight": "Weight (kg)",
            "reps": "Repetitions",
        }
        widgets = {
            "weight": forms.NumberInput(
                attrs={
                    "step": "0.5",
                    "min": "0",
                    "class": "form-control",
                    "placeholder": "e.g. 100",
                }
            ),
            "reps": forms.NumberInput(
                attrs={
                    "min": "1",
                    "max": "30",
                    "class": "form-control",
                    "placeholder": "e.g. 5",
                }
            ),
            "exercise": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("exercise", css_class="col-md-6"),
            ),
            Row(
                Column("weight", css_class="col-md-6"),
                Column("reps", css_class="col-md-6"),
            ),
            Submit("submit", "Save Set", css_class="btn btn-primary btn-block mt-3"),
        )

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get("weight")
        reps = cleaned_data.get("reps")

        if weight is not None and weight <= 0:
            raise forms.ValidationError("Weight must be greater than 0")
        if reps is not None and (reps < 1 or reps > 30):
            raise forms.ValidationError("Repetitions must be between 1 and 30")

        return cleaned_data
