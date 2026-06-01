from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.permissions import IsAuthenticated
from .models import Item, Notification
from .serializers import ItemSerializer
from django.contrib import messages
from django.http import HttpResponseForbidden
import requests
from decimal import Decimal

def get_accept_format(request):
    accept_header = request.META.get('HTTP_ACCEPT', 'text/html')
    format_param = request.GET.get('format', None)

    if format_param == 'json':
        return 'json'
    if 'application/json' in accept_header:
        return 'json'
    return 'html'

@require_http_methods(["POST"])
def nominatim_proxy(request):
    """Server-side proxy for Nominatim reverse geocoding API.

    Handles CORS, firewall restrictions, and custom User-Agent header.
    Frontend sends latitude and longitude; backend fetches address and returns JSON.
    """
    try:
        lat_str = request.POST.get('latitude', '').strip()
        lng_str = request.POST.get('longitude', '').strip()

        if not lat_str or not lng_str:
            return JsonResponse({'error': 'Missing coordinates'}, status=400)

        lat = Decimal(lat_str)
        lng = Decimal(lng_str)

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return JsonResponse({'error': 'Invalid coordinate range'}, status=400)

        nominatim_url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}'

        response = requests.get(
            nominatim_url,
            headers={
                'User-Agent': 'EcoTrack-Marketplace/1.0',
                'Accept': 'application/json',
            },
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        return JsonResponse(data)

    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Nominatim request timeout'}, status=503)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Nominatim API error: {str(e)}'}, status=502)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid coordinates format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def item_list_view(request):
    if get_accept_format(request) == 'json':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)

    items = Item.objects.all()
    context = {'items': items}
    return render(request, 'items/item_list.html', context)


def home_view(request):
    """Homepage: reuse the item list view for the public landing.

    Logic:
    - If the user is authenticated (still logged in), send them to the canonical
      items list so they resume where they left off.
    - Otherwise render the public items listing (same as `item_list_view`).
    """
    if request.user.is_authenticated:
        return redirect('item_list')
    return item_list_view(request)


@login_required
@require_http_methods(["POST"])
def item_delete_view(request, pk):
    """Allow the donor to delete their posted item.

    Only accepts POST to avoid accidental deletes via GET.
    """
    item = get_object_or_404(Item, pk=pk)

    if item.donor != request.user:
        return HttpResponseForbidden('You are not allowed to delete this item.')

    try:
        item.delete()
        messages.success(request, 'Item deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting item: {e}')

    return redirect('dashboard')

def item_detail_view(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if get_accept_format(request) == 'json':
        serializer = ItemSerializer(item)
        return JsonResponse(serializer.data)

    context = {'item': item}
    return render(request, 'items/item_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def item_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        address = request.POST.get('address', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()

        if not all([title, description, image]):
            messages.error(request, 'Title, description, and image are required.')
            context = {'form_data': request.POST}
            return render(request, 'items/item_form.html', context, status=400)

        if not latitude or not longitude:
            messages.error(request, "Please click 'Detect My Current Location' to set your location.")
            context = {'form_data': request.POST}
            return render(request, 'items/item_form.html', context, status=400)

        if not address:
            messages.error(request, "Please provide an address (auto-filled by location detection or enter manually).")
            context = {'form_data': request.POST}
            return render(request, 'items/item_form.html', context, status=400)

        try:
            item = Item.objects.create(
                title=title,
                description=description,
                image=image,
                latitude=latitude,
                longitude=longitude,
                address=address,
                contact_number=contact_number,
                donor=request.user
            )
            return redirect('item_list')
        except Exception as e:
            messages.error(request, f'Error creating item: {str(e)}')
            context = {'form_data': request.POST}
            return render(request, 'items/item_form.html', context, status=400)

    return render(request, 'items/item_form.html')

class ItemClaimAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.donor == request.user:
            return Response(
                {'error': 'You cannot claim your own item.'},
                status=HTTP_403_FORBIDDEN
            )

        if item.claimant is not None:
            return Response(
                {'error': 'This item has already been claimed.'},
                status=HTTP_400_BAD_REQUEST
            )

        item.claimant = request.user
        item.status = 'PENDING'
        item.save()

        Notification.objects.create(
            recipient=item.donor,
            notification_type='ITEM_CLAIMED',
            item=item,
            actor=request.user
        )

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=HTTP_200_OK)


class ItemApproveClaimAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.donor != request.user:
            return Response(
                {'error': 'Only the donor can approve claims.'},
                status=HTTP_403_FORBIDDEN
            )

        if item.status != 'PENDING':
            return Response(
                {'error': 'Item must be in PENDING status to approve.'},
                status=HTTP_400_BAD_REQUEST
            )

        item.status = 'COLLECTED'
        item.save()

        Notification.objects.create(
            recipient=item.claimant,
            notification_type='CLAIM_APPROVED',
            item=item,
            actor=request.user
        )

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=HTTP_200_OK)


class ItemRejectClaimAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)

        if item.donor != request.user:
            return Response(
                {'error': 'Only the donor can reject claims.'},
                status=HTTP_403_FORBIDDEN
            )

        if item.status != 'PENDING':
            return Response(
                {'error': 'Item must be in PENDING status to reject.'},
                status=HTTP_400_BAD_REQUEST
            )

        claimant = item.claimant
        item.claimant = None
        item.status = 'AVAILABLE'
        item.save()

        Notification.objects.create(
            recipient=claimant,
            notification_type='CLAIM_REJECTED',
            item=item,
            actor=request.user
        )

        serializer = ItemSerializer(item)
        return Response(serializer.data, status=HTTP_200_OK)


@login_required
def user_dashboard_view(request):
    donated_items = request.user.donated_items.all()
    claimed_items = request.user.claimed_items.all()
    pending_approvals = request.user.donated_items.filter(status='PENDING')
    notifications = request.user.notifications.all()
    unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'donated_items': donated_items,
        'claimed_items': claimed_items,
        'pending_approvals': pending_approvals,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'user_dashboard.html', context)


class UserNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = request.user.notifications.all()
        unread_count = request.user.notifications.filter(is_read=False).count()

        data = {
            'unread_count': unread_count,
            'notifications': [
                {
                    'id': n.id,
                    'type': n.notification_type,
                    'item_title': n.item.title,
                    'actor': n.actor.username,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                }
                for n in notifications
            ]
        }
        return Response(data, status=HTTP_200_OK)


class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'}, status=HTTP_200_OK)
