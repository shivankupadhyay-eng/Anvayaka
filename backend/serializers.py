from rest_framework import serializers
from .models import Labour, Stock, Parchi, Task, UserProfile

class LabourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labour
        fields = '__all__'
    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class ParchiSerializer(serializers.ModelSerializer):
    task=serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    labour = serializers.PrimaryKeyRelatedField(queryset=Labour.objects.all())   
    class Meta:
        model = Parchi
        fields = ['id', 'task', 'labour', 'details', 'deliverable', 'deadline']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class mqtt_updated_data(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','completed_quantity']