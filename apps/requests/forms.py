from django import forms

from apps.requests.models import Request, RequestComment, RequestPriority


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["title", "description", "category", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }


class RequestFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}))
    category = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={"class": "form-select"})
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[("", "All")] + list(RequestPriority.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop("categories", [])
        statuses = kwargs.pop("statuses", [])
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [("", "All")] + statuses
        self.fields["category"].choices = [("", "All")] + [(c.id, c.name) for c in categories]


class CommentForm(forms.ModelForm):
    class Meta:
        model = RequestComment
        fields = ["body", "is_internal"]
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_internal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CancelForm(forms.Form):
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


class ApprovalCommentForm(forms.Form):
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
