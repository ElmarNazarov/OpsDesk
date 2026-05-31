from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.approvals.forms import ApprovalCommentForm
from apps.approvals.permissions import user_can_approve_request, user_can_reject_request
from apps.approvals.services import approve_request, reject_request
from apps.core.exceptions import InvalidStateError, PermissionDeniedError
from apps.requests.forms import CancelForm, CommentForm, RequestFilterForm, RequestForm
from apps.requests.models import Request, RequestStatus
from apps.requests.permissions import (
    require_can_view_request,
    user_can_edit_request,
)
from apps.requests.selectors import (
    filter_requests,
    get_active_categories,
    get_comments_for_request,
    get_request_by_public_id,
    get_requests_for_user,
)
from apps.requests.services import (
    add_request_comment,
    cancel_request,
    create_request,
    submit_request,
)


@login_required
def request_list(request):
    qs = get_requests_for_user(request.user)
    categories = get_active_categories()
    filter_form = RequestFilterForm(
        request.GET or None,
        categories=categories,
        statuses=list(RequestStatus.choices),
    )
    if filter_form.is_valid():
        qs = filter_requests(
            qs,
            status=filter_form.cleaned_data.get("status") or None,
            category=filter_form.cleaned_data.get("category") or None,
            priority=filter_form.cleaned_data.get("priority") or None,
        )
    return render(
        request,
        "requests/list.html",
        {"requests": qs, "filter_form": filter_form},
    )


@login_required
def request_create(request):
    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            req = create_request(
                request.user,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                category=form.cleaned_data["category"],
                priority=form.cleaned_data["priority"],
            )
            messages.success(request, f"Draft request {req.public_id} created.")
            return redirect("requests:detail", public_id=req.public_id)
    else:
        form = RequestForm()
    form.fields["category"].queryset = get_active_categories()
    return render(request, "requests/form.html", {"form": form, "title": "New Request"})


@login_required
def request_detail(request, public_id):
    req = get_request_by_public_id(public_id)
    if not req:
        raise Http404
    try:
        require_can_view_request(request.user, req)
    except PermissionDenied:
        raise Http404 from None
    comments = get_comments_for_request(request.user, req)
    comment_form = CommentForm()
    cancel_form = CancelForm()
    approval_form = ApprovalCommentForm()
    can_edit = user_can_edit_request(request.user, req)
    can_approve = user_can_approve_request(request.user, req)
    can_reject = user_can_reject_request(request.user, req)
    return render(
        request,
        "requests/detail.html",
        {
            "request_obj": req,
            "comments": comments,
            "comment_form": comment_form,
            "cancel_form": cancel_form,
            "approval_form": approval_form,
            "can_edit": can_edit,
            "can_approve": can_approve,
            "can_reject": can_reject,
            "status_history": req.status_history.select_related("changed_by"),
        },
    )


@login_required
def request_edit(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    if not user_can_edit_request(request.user, req):
        raise Http404
    if request.method == "POST":
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated.")
            return redirect("requests:detail", public_id=public_id)
    else:
        form = RequestForm(instance=req)
    form.fields["category"].queryset = get_active_categories()
    return render(request, "requests/form.html", {"form": form, "title": f"Edit {public_id}"})


@login_required
def request_submit(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    try:
        submit_request(request.user, req, http_request=request)
        messages.success(request, "Request submitted successfully.")
    except (PermissionDeniedError, InvalidStateError) as e:
        messages.error(request, str(e))
    return redirect("requests:detail", public_id=public_id)


@login_required
def request_cancel(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    if request.method == "POST":
        form = CancelForm(request.POST)
        if form.is_valid():
            try:
                cancel_request(
                    request.user,
                    req,
                    reason=form.cleaned_data.get("reason", ""),
                    http_request=request,
                )
                messages.success(request, "Request cancelled.")
            except PermissionDeniedError as e:
                messages.error(request, str(e))
    return redirect("requests:detail", public_id=public_id)


@login_required
def request_comment(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                add_request_comment(
                    request.user,
                    req,
                    body=form.cleaned_data["body"],
                    is_internal=form.cleaned_data.get("is_internal", False),
                    http_request=request,
                )
                messages.success(request, "Comment added.")
            except PermissionDeniedError as e:
                messages.error(request, str(e))
    return redirect("requests:detail", public_id=public_id)


@login_required
def request_approve(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    if request.method == "POST":
        form = ApprovalCommentForm(request.POST)
        comment = form.cleaned_data.get("comment", "") if form.is_valid() else ""
        try:
            approve_request(request.user, req, comment=comment, http_request=request)
            messages.success(request, "Request approved.")
        except (PermissionDeniedError, InvalidStateError) as e:
            messages.error(request, str(e))
    return redirect("requests:detail", public_id=public_id)


@login_required
def request_reject(request, public_id):
    req = get_object_or_404(Request, public_id=public_id)
    if request.method == "POST":
        form = ApprovalCommentForm(request.POST)
        comment = form.cleaned_data.get("comment", "") if form.is_valid() else ""
        try:
            reject_request(request.user, req, comment=comment, http_request=request)
            messages.success(request, "Request rejected.")
        except (PermissionDeniedError, InvalidStateError) as e:
            messages.error(request, str(e))
    return redirect("requests:detail", public_id=public_id)
