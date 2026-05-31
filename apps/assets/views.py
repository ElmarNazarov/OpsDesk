from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.assets.forms import AssetForm, AssignAssetForm
from apps.assets.models import Asset
from apps.assets.permissions import user_can_assign_assets, user_can_manage_assets
from apps.assets.selectors import get_assets_for_ops, get_fulfillment_queue
from apps.assets.services import assign_asset_to_employee, fulfill_equipment_request
from apps.core.exceptions import InvalidStateError, PermissionDeniedError
from apps.dashboard.selectors import get_ops_dashboard_context


@login_required
def ops_dashboard(request):
    if not (request.user.is_ops or request.user.is_admin_role):
        raise PermissionDenied
    ctx = get_ops_dashboard_context()
    return render(request, "ops/dashboard.html", ctx)


@login_required
def ops_fulfillment(request):
    if not (request.user.is_ops or request.user.is_admin_role):
        raise PermissionDenied
    return render(
        request,
        "ops/fulfillment.html",
        {"fulfillment_queue": get_fulfillment_queue()},
    )


@login_required
def ops_asset_list(request):
    if not user_can_manage_assets(request.user):
        raise PermissionDenied
    return render(request, "ops/asset_list.html", {"assets": get_assets_for_ops()})


@login_required
def ops_asset_create(request):
    if not user_can_manage_assets(request.user):
        raise PermissionDenied
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset created.")
            return redirect("ops:asset_list")
    else:
        form = AssetForm()
    return render(request, "ops/asset_form.html", {"form": form, "title": "New Asset"})


@login_required
def ops_asset_detail(request, pk):
    if not user_can_manage_assets(request.user):
        raise PermissionDenied
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "ops/asset_detail.html", {"asset": asset})


@login_required
def ops_asset_assign(request, pk):
    if not user_can_assign_assets(request.user):
        raise PermissionDenied
    asset = get_object_or_404(Asset, pk=pk)
    request_id = request.GET.get("request")
    related_request = None
    if request_id:
        from apps.requests.models import Request

        related_request = Request.objects.filter(public_id=request_id).first()

    if request.method == "POST":
        form = AssignAssetForm(request.POST)
        if form.is_valid():
            try:
                if related_request and related_request.category.slug == "equipment":
                    fulfill_equipment_request(
                        request.user,
                        related_request,
                        asset,
                        http_request=request,
                    )
                    messages.success(request, "Equipment request fulfilled.")
                    return redirect("ops:fulfillment")
                assign_asset_to_employee(
                    asset,
                    form.cleaned_data["employee"],
                    request.user,
                    related_request=related_request,
                    notes=form.cleaned_data.get("notes", ""),
                    http_request=request,
                )
                messages.success(request, "Asset assigned.")
                return redirect("ops:asset_detail", pk=pk)
            except (PermissionDeniedError, InvalidStateError) as e:
                messages.error(request, str(e))
    else:
        form = AssignAssetForm()
        if related_request:
            form.fields["employee"].initial = related_request.requester
    return render(
        request,
        "ops/asset_assign.html",
        {"asset": asset, "form": form, "related_request": related_request},
    )
