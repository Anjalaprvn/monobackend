from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import Booking
from slots.models import Slot
import json
import uuid


def booking_list_html(request):
    """
    HTML view to display list of bookings
    """
    # Get bookings from the booking app
    bookings = Booking.objects.all().order_by('-created_at')
    
    # Get booked slots from the slots app that don't have corresponding bookings
    from slots.models import Slot
    
    # We'll now combine bookings and booked slots, avoiding duplicates
    # For each booking, check if there's a corresponding slot in the slots app
    # Only show entries that don't have duplicates
    
    # Calculate statistics
    unique_slots = Slot.objects.filter(bookings__isnull=False).distinct().count()
    recent_bookings = bookings.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    
    context = {
        'bookings': bookings,
        'app_name': 'booking',
        'model_name': 'Booking',
        'current_page': 'bookings'
    }
    return render(request, 'booking/list.html', context)


def booking_detail_html(request, pk):
    """
    HTML view to display details of a specific booking
    """
    try:
        booking = Booking.objects.get(pk=pk)
        context = {
            'booking': booking,
            'app_name': 'booking',
            'model_name': 'Booking'
        }
        return render(request, 'booking/view.html', context)
    except Booking.DoesNotExist:
        from django.http import Http404
        raise Http404("Booking does not exist")


def booking_add_html(request):
    """
    HTML view to add a new booking
    """
    # Get date parameter if provided
    selected_date = request.GET.get('date', '')
    
    # Import slots model from slots app
    from slots.models import Slot
    
    # Filter available slots by date if provided, otherwise get all available slots
    if selected_date:
        available_slots = Slot.objects.filter(is_booked=False, date=selected_date)
    else:
        available_slots = Slot.objects.filter(is_booked=False)
    
    context = {
        'available_slots': available_slots,
        'selected_date': selected_date,
        'app_name': 'booking',
        'model_name': 'Booking'
    }
    return render(request, 'booking/add.html', context)


def booking_edit_html(request, pk):
    """
    HTML view to edit a specific booking
    """
    try:
        booking = Booking.objects.get(pk=pk)
        available_slots = Slot.objects.all()  # All slots available for editing
        context = {
            'booking': booking,
            'available_slots': available_slots,
            'app_name': 'booking',
            'model_name': 'Booking'
        }
        return render(request, 'booking/edit.html', context)
    except Booking.DoesNotExist:
        from django.http import Http404
        raise Http404("Booking does not exist")


@csrf_exempt
def delete_booking_html(request, pk):
    """
    POST /booking/<uuid:pk>/delete/ - deletes an existing booking
    """
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(pk=pk)
            booking.delete()
            from django.shortcuts import redirect
            return JsonResponse({'success': True, 'message': 'Booking deleted successfully'})
        except Booking.DoesNotExist:
            from django.shortcuts import redirect
            return JsonResponse({'success': False, 'error': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    from django.shortcuts import redirect
    return redirect('booking:booking_list')


def slot_list_html(request):
    """
    HTML view to display list of booking slots
    """
    slots = Slot.objects.all().order_by('-created_at')
    context = {
        'slots': slots,
        'app_name': 'booking',
        'model_name': 'Slot'
    }
    return render(request, 'booking/slot_list.html', context)


def slot_add_html(request):
    """
    HTML view to add a new booking slot
    """
    context = {
        'app_name': 'booking',
        'model_name': 'Slot'
    }
    return render(request, 'booking/slot_add.html', context)


def slot_detail_html(request, pk):
    """
    HTML view to display details of a specific booking slot
    """
    try:
        slot = Slot.objects.get(pk=pk)
        context = {
            'slot': slot,
            'app_name': 'booking',
            'model_name': 'Slot'
        }
        return render(request, 'booking/slot_view.html', context)
    except Slot.DoesNotExist:
        from django.http import Http404
        raise Http404("Booking Slot does not exist")


def slot_edit_html(request, pk):
    """
    HTML view to edit a specific booking slot
    """
    try:
        slot = Slot.objects.get(pk=pk)
        context = {
            'slot': slot,
            'app_name': 'booking',
            'model_name': 'Slot'
        }
        return render(request, 'booking/slot_edit.html', context)
    except Slot.DoesNotExist:
        from django.http import Http404
        raise Http404("Booking Slot does not exist")


@csrf_exempt
def delete_slot(request, pk):
    """
    POST /booking/slots/<uuid:pk>/delete/ - deletes an existing booking slot
    """
    if request.method == 'POST':
        try:
            slot = Slot.objects.get(pk=pk)
            slot.delete()
            from django.shortcuts import redirect
            return redirect('booking:slot_list')
        except Slot.DoesNotExist:
            from django.shortcuts import redirect
            return redirect('booking:slot_list')
        except Exception:
            from django.shortcuts import redirect
            return redirect('booking:slot_list')
    
    from django.shortcuts import redirect
    return redirect('booking:slot_list')


@csrf_exempt
def book_slot(request, pk):
    """
    POST /booking/slots/<uuid:pk>/book/ - books a slot
    """
    if request.method == 'POST':
        try:
            slot = Slot.objects.get(pk=pk)
            
            # Check if slot is available
            if slot.is_booked:
                return JsonResponse({
                    'success': False,
                    'error': 'Slot is not available for booking'
                }, status=400)
            
            # Get booking data
            data = json.loads(request.body)
            
            # Create booking
            booking = Booking.objects.create(
                slot=slot,
                name=data.get('name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                notes=data.get('notes', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Slot booked successfully',
                'booking_id': str(booking.id)
            })
                
        except BookingSlot.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Slot not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# API Views
@csrf_exempt
def booking_list(request):
    """
    GET /api/bookings/ - returns JSON list of bookings
    """
    if request.method == 'GET':
        bookings = Booking.objects.all().order_by('-created_at')
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': str(booking.id),
                'slot_name': booking.slot.name,
                'name': booking.name,
                'email': booking.email,
                'phone': booking.phone,
                'notes': booking.notes,
                'created_at': booking.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'count': len(booking_data),
            'bookings': booking_data
        })


@csrf_exempt
def create_booking(request):
    """
    POST /api/bookings/create/ - creates a new booking
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slot_id = data.get('slot')  # Changed from 'slot_id' to 'slot'
            
            # Get the slot from the slots app
            try:
                from slots.models import Slot
                slot_obj = Slot.objects.get(id=slot_id)
            except Slot.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Slot not found'
                }, status=404)
            
            # Check if slot is available
            if slot_obj.is_booked:
                return JsonResponse({
                    'success': False,
                    'error': 'Slot is not available'
                }, status=400)
            
            # Create a corresponding BookingSlot in the booking app if it doesn't exist
            booking_slot, created = BookingSlot.objects.get_or_create(
                name=slot_obj.name,
                date=slot_obj.date,
                start_time=slot_obj.start_time,
                end_time=slot_obj.end_time,
                defaults={
                    'description': slot_obj.description,
                    'is_available': False
                }
            )
            
            # If the booking slot was not newly created, mark it as unavailable
            if not created:
                booking_slot.is_available = False
                booking_slot.save()
            
            # Create booking
            booking = Booking.objects.create(
                slot=booking_slot,
                name=data.get('name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                notes=data.get('notes', '')
            )
            
            # Update the original slot to booked status
            slot_obj.is_booked = True
            slot_obj.booked_by = data.get('name', '')
            slot_obj.notes = data.get('notes', '')
            slot_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking created successfully',
                'booking_id': str(booking.id)
            }, status=201)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_booking(request, pk):
    """
    PUT /api/bookings/{id}/update/ - updates an existing booking
    """
    if request.method == 'PUT':
        try:
            booking = Booking.objects.get(pk=pk)
            data = json.loads(request.body)
            
            # Update booking fields
            if 'name' in data:
                booking.name = data['name']
            if 'email' in data:
                booking.email = data['email']
            if 'phone' in data:
                booking.phone = data['phone']
            if 'notes' in data:
                booking.notes = data['notes']
            if 'slot' in data:
                try:
                    slot = BookingSlot.objects.get(id=data['slot'])
                    booking.slot = slot
                except BookingSlot.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Slot not found'
                    }, status=404)
            
            booking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking updated successfully'
            })
                
        except Booking.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def slot_list(request):
    """
    GET /api/slots/ - returns JSON list of booking slots
    """
    if request.method == 'GET':
        slots = BookingSlot.objects.all().order_by('-created_at')
        slot_data = []
        for slot in slots:
            slot_data.append({
                'id': str(slot.id),
                'name': slot.name,
                'description': slot.description,
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'date': slot.date.isoformat(),
                'is_available': slot.is_available,
                'created_at': slot.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'count': len(slot_data),
            'slots': slot_data
        })


@csrf_exempt
def create_slot(request):
    """
    POST /api/slots/create/ - creates a new booking slot
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            slot = BookingSlot.objects.create(
                name=data.get('name', ''),
                description=data.get('description', ''),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                date=data.get('date')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Slot created successfully',
                'slot_id': str(slot.id)
            }, status=201)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_slot(request, pk):
    """
    PUT /api/slots/{id}/update/ - updates an existing booking slot
    """
    if request.method == 'PUT':
        try:
            slot = BookingSlot.objects.get(pk=pk)
            data = json.loads(request.body)
            
            # Update slot fields
            if 'name' in data:
                slot.name = data['name']
            if 'description' in data:
                slot.description = data['description']
            if 'start_time' in data:
                slot.start_time = data['start_time']
            if 'end_time' in data:
                slot.end_time = data['end_time']
            if 'date' in data:
                slot.date = data['date']
            if 'is_available' in data:
                slot.is_available = data['is_available']
            
            slot.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Slot updated successfully'
            })
                
        except BookingSlot.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Slot not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_available_slots_for_date(request):
    """
    GET /api/bookings/available-slots/?date=YYYY-MM-DD - returns available slots for a specific date
    """
    if request.method == 'GET':
        date_param = request.GET.get('date', '')
        
        if not date_param:
            return JsonResponse({
                'success': False,
                'error': 'Date parameter is required'
            }, status=400)
        
        try:
            # Import slots model from slots app
            from slots.models import Slot
            
            available_slots = Slot.objects.filter(is_booked=False, date=date_param)
            slot_data = []
            
            for slot in available_slots:
                slot_data.append({
                    'id': str(slot.id),
                    'name': slot.name,
                    'description': slot.description,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'date': slot.date.strftime('%Y-%m-%d'),
                    'display_text': f"{slot.name} - {slot.date.strftime('%b %d, %Y')} ({slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')})"
                })
            
            return JsonResponse({
                'success': True,
                'count': len(slot_data),
                'slots': slot_data
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_booking(request, pk):
    """
    DELETE /api/bookings/{id}/delete/ - deletes an existing booking
    """
    if request.method == 'DELETE':
        try:
            booking = Booking.objects.get(pk=pk)
            booking.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking deleted successfully'
            })
                
        except Booking.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
