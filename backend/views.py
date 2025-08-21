# core/views.py
from rest_framework import viewsets
from .models import Labour, Stock, UserProfile, Task, Parchi
from .serializers import LabourSerializer, StockSerializer, UserProfileSerializer, TaskSerializer, ParchiSerializer
import subprocess
import signal
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

class LabourViewSet(viewsets.ModelViewSet):
    queryset = Labour.objects.all()
    serializer_class = LabourSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class ParchiViewSet(viewsets.ModelViewSet):
    queryset = Parchi.objects.all()
    serializer_class = ParchiSerializer


mqtt_process = None

@csrf_exempt
@require_http_methods(["POST"])
def start_mqtt_listener(request):
    global mqtt_process
    
    try:
        if mqtt_process and mqtt_process.poll() is None:
            return JsonResponse({
                'status': 'error',
                'message': 'MQTT listener is already running',
                'pid': mqtt_process.pid
            })
        
        # Start the MQTT listener as a subprocess
        mqtt_process = subprocess.Popen([
            'python', 'manage.py', 'run_mqtt_listener'
        ], cwd=os.getcwd())
        
        return JsonResponse({
            'status': 'success',
            'message': 'MQTT listener started successfully',
            'pid': mqtt_process.pid
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to start MQTT listener: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def stop_mqtt_listener(request):
    global mqtt_process
    
    try:
        if not mqtt_process or mqtt_process.poll() is not None:
            return JsonResponse({
                'status': 'error',
                'message': 'MQTT listener is not running'
            })
        
        # Terminate the process
        mqtt_process.terminate()
        mqtt_process.wait(timeout=10)  # Wait up to 10 seconds
        
        return JsonResponse({
            'status': 'success',
            'message': 'MQTT listener stopped successfully'
        })
        
    except subprocess.TimeoutExpired:
        # Force kill if it doesn't terminate gracefully
        mqtt_process.kill()
        return JsonResponse({
            'status': 'success',
            'message': 'MQTT listener force stopped'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to stop MQTT listener: {str(e)}'
        })

@require_http_methods(["GET"])
def mqtt_listener_status(request):
    global mqtt_process
    
    if mqtt_process and mqtt_process.poll() is None:
        status = 'running'
        pid = mqtt_process.pid
    else:
        status = 'stopped'
        pid = None
    
    return JsonResponse({
        'status': status,
        'pid': pid
    })