from django.db import models
from .chatbot_logic import get_medical_advice
from django.conf import settings


class Doctor(models.Model):
    name      = models.CharField(max_length=200)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"


class Patient(models.Model):
    user    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name    = models.CharField(max_length=200)
    address = models.CharField(max_length=200)   # increased from 20
    age     = models.IntegerField()
    profile_complete = models.BooleanField(default=False) 
# Add default=False here
    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    patient      = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='chats')
    user_message = models.TextField()
    ai_response  = models.TextField()
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class Appointment(models.Model):
    patient    = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor     = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    date       = models.DateField()
    time_slot  = models.TimeField()
    symptoms   = models.TextField()

    ai_predicted_disease = models.CharField(max_length=200, blank=True)
    ai_precaution        = models.TextField(blank=True)
    ai_assigned_doctor   = models.BooleanField(default=False)  # flag: did AI pick the doctor?

    class Meta:
        unique_together = ('doctor', 'date', 'time_slot')

    def save(self, *args, **kwargs):
        # Run AI analysis on symptoms every time
        suggested_spec, prediction, precaution = get_medical_advice(self.symptoms)
        self.ai_predicted_disease = prediction
        self.ai_precaution        = precaution

        # Auto-assign doctor ONLY when none was manually chosen
        if not self.doctor_id:
            suggested_doctor = Doctor.objects.filter(specialty__icontains=suggested_spec).first()
            if not suggested_doctor:
                # Fallback: grab any available doctor
                suggested_doctor = Doctor.objects.first()
            if suggested_doctor:
                self.doctor           = suggested_doctor
                self.ai_assigned_doctor = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} → {self.doctor} on {self.date}"
