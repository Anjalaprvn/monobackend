from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Slot
from .serializers import SlotSerializer
from booking.models import Booking
import json
import uuid
from datetime import datetime
from django.utils import timezone


def slot_list_html(request):
    # Get filter parameters
    date_filter = request.GET.get('date', '')
    
    # Start with all slots
    slots = Slot.objects.all()
    
    # Apply date filter if provided
    if date_filter:
        slots = slots.filter(date=date_filter)
    
    # Order by date ascending (earliest first), then by start time
    slots = slots.order_by('date', 'start_time')
    
    context = {
        'slots': slots,
        'model_name': 'Time Slot',
        'date_filter': date_filter,
        'current_page': 'slots'
    }
    return render(request, 'slots/list.html', context)


def slot_add_html(request):
    context = {
        'model_name': 'Time Slot'
    }
    return render(request, 'slots/add.html', context)


def slot_detail_html(request, pk):
    slot = get_object_or_404(Slot, pk=pk)
    context = {
        'slot': slot,
        'model_name': 'Time Slot'
    }
    return render(request, 'slots/detail.html', context)


def slot_edit_html(request, pk):
    slot = get_object_or_404(Slot, pk=pk)
    context = {
        'slot': slot,
        'model_name': 'Time Slot'
    }
    return render(request, 'slots/edit.html', context)


def delete_slot(request, pk):
    if request.method == 'POST':
        try:
            slot = get_object_or_404(Slot, pk=pk)
            slot.delete()
            # Return JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Slot deleted successfully'})
            else:
                return redirect('slots:slot_list')
        except Exception as e:
            # Return JSON error response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                return redirect('slots:slot_list')
    # For non-POST requests, redirect to list page
    return redirect('slots:slot_list')


@csrf_exempt
def unbook_slot(request, pk):
    """POST /slots/<uuid:pk>/unbook/ - unbooks a slot and removes associated booking"""
    if request.method == 'POST':
        try:
            slot = get_object_or_404(Slot, pk=pk)
            
            # Update the slot to available status
            slot.status = 'available'
            slot.booked_by = ''
            slot.notes = ''
            slot.save()
            
            # Also try to remove the corresponding booking
            # Delete all bookings for this slot
            Booking.objects.filter(slot=slot).delete()
            # Mark the slot as available
            slot.status = 'available'
            slot.booked_by = ''
            slot.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Slot unbooked successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def slot_list_api(request):
    """GET /api/slots/ - returns list of all slots"""
    if request.method == 'GET':
        try:
            slots = Slot.objects.all().order_by('date', 'start_time')
            serializer = SlotSerializer(slots, many=True)
            
            response_data = {
                'success': True,
                'count': slots.count(),
                'slots': serializer.data
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_slot_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # Required fields
        required_fields = ['name', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'success': False, 'error': f'{field} is required'}, status=400)

        # Create slot without status
        slot = Slot.objects.create(
            name=data['name'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            booked_by=data.get('booked_by', ''),
            notes=data.get('notes', ''),
            is_booked=data.get('is_booked', False)  # optional
        )

        return JsonResponse({'success': True, 'slot': SlotSerializer(slot).data}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def update_slot_api(request, pk):
    if request.method == 'PUT':
        try:
            slot = get_object_or_404(Slot, pk=pk)
            data = json.loads(request.body)
            
            # Update fields if provided
            if 'name' in data:
                slot.name = data['name']
            if 'date' in data:
                slot.date = data['date']
            if 'start_time' in data:
                slot.start_time = data['start_time']
            if 'end_time' in data:
                slot.end_time = data['end_time']
            if 'status' in data:
                slot.status = data['status']
            if 'description' in data:
                slot.description = data['description']
            if 'booked_by' in data:
                slot.booked_by = data['booked_by']
            if 'notes' in data:
                slot.notes = data['notes']
            
            slot.save()
            
            return JsonResponse({'success': True, 'slot': SlotSerializer(slot).data})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Slot.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Slot not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def book_slot_html(request, pk):
    slot = get_object_or_404(Slot, pk=pk)
    context = {
        'slot': slot,
        'model_name': 'Time Slot'
    }
    return render(request, 'slots/book.html', context)


@csrf_exempt
def book_slot_api(request, pk):
    if request.method == 'POST':
        try:
            slot = get_object_or_404(Slot, pk=pk)
            data = json.loads(request.body)
            
            # Check if slot is available
            if slot.status != 'available':
                return JsonResponse({'success': False, 'error': 'Slot is not available'}, status=400)
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'error': f'{field} is required'}, status=400)
            
            # Update the slot to booked status and assign customer info
            slot.status = 'booked'
            slot.booked_by = data['name']
            slot.notes = data.get('notes', '')
            slot.save()
            
            # Also create a booking record in the booking app
            try:
                # Create the booking using the existing slot
                booking = Booking.objects.create(
                    slot=slot,
                    name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    notes=data.get('notes', '')
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Slot booked successfully',
                    'booking_id': str(booking.id)
                })
            except Exception as e:
                # If booking creation fails, still return success for the slot booking
                # but log the error
                print(f"Error creating booking: {e}")
                return JsonResponse({'success': True, 'message': 'Slot booked successfully'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Slot.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Slot not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)