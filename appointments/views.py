from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Doctor, Patient
from .chatbot_logic import get_medical_advice


# ─────────────────── PUBLIC PAGES ───────────────────

def home(request):
    doctors = Doctor.objects.all()[:3]
    return render(request, 'appointments/home.html', {'doctors': doctors})

def about(request):
    doctors = Doctor.objects.all()
    return render(request, 'appointments/about.html', {'doctors': doctors})

def patients(request):
    return render(request, 'appointments/patients.html')

def rates(request):
    return render(request, 'appointments/rates.html')

def contact(request):
    return render(request, 'appointments/contacts.html')


# ─────────────────── BOOKING ────────────────────────
@login_required
def book_appointment(request):
    existing_patient = getattr(request.user, 'patient', None)

    form_data = {
        'name': existing_patient.name if existing_patient else '',
        'age': existing_patient.age if existing_patient else '',
        'address': existing_patient.address if existing_patient else '',
    }

    if request.method == "POST":
        # Extract data from POST
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        symptoms = request.POST.get('symptoms')
        
        # 1. Validation Check: Prevent Double Booking
        # We check if an appointment already exists for this doctor/date/time
        if doctor_id:
            exists = Appointment.objects.filter(
                doctor_id=doctor_id, 
                date=date, 
                time_slot=time_slot
            ).exists()
            
            if exists:
                messages.error(request, "This doctor is already booked for this time slot. Please choose another time.")
                # Return the form with the user's data so they don't have to re-type symptoms
                return render(request, 'appointments/book_appointment.html', {
                    'doctors': Doctor.objects.all(),
                    'form_data': request.POST,
                    'patient': existing_patient,
                })

        # 2. Proceed with saving if slot is available
        try:
            # Update/Create Patient logic
            if existing_patient:
                patient = existing_patient
                patient.name = request.POST.get('name')
                patient.age = int(request.POST.get('age'))
                patient.address = request.POST.get('address')
                patient.save()
            else:
                patient = Patient.objects.create(
                    user=request.user, 
                    name=request.POST.get('name'), 
                    age=int(request.POST.get('age')), 
                    address=request.POST.get('address')
                )

            # Create the appointment (AI logic triggers in models.py)
            appointment = Appointment.objects.create(
                patient=patient,
                doctor_id=doctor_id if doctor_id else None,
                date=date,
                time_slot=time_slot,
                symptoms=symptoms
            )

            request.session['last_appointment_id'] = appointment.id
            return redirect('appointment_success')

        except ValueError:
            messages.error(request, "Please enter a valid age.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, 'appointments/book_appointment.html', {
        'doctors': Doctor.objects.all(),
        'form_data': form_data,
        'patient': existing_patient,
    })

@login_required
def appointment_success(request):
    # 1. Fetch the ID we just saved in the session
    appt_id = request.session.get('last_appointment_id')
    
    if not appt_id:
        # If someone tries to visit /success/ directly without booking, send them back
        return redirect('book_appointment')

    # 2. Get the appointment from the database (including the AI results)
    appointment = get_object_or_404(Appointment, pk=appt_id)
    
    # 3. Send the appointment object to the HTML
    return render(request, 'appointments/appointment_success.html', {
        'appointment': appointment,
    })

# ─────────────────── CHATBOT ────────────────────────

@login_required
def chatbot_view(request):
    from .models import ChatMessage
    chat_history = ChatMessage.objects.filter(patient=request.user.patient)
    analysis = None

    if request.method == "POST":
        symptoms = request.POST.get('symptoms')
        _, diagnosis, precautions = get_medical_advice(symptoms)
        analysis = {'diagnosis': diagnosis, 'precautions': precautions}

        ChatMessage.objects.create(
            patient      = request.user.patient,
            user_message = symptoms,
            ai_response  = f"Diagnosis: {diagnosis}\nPrecautions: {precautions}",
        )

    return render(request, 'appointments/chatbot.html', {
        'analysis':     analysis,
        'chat_history': chat_history,
    })
