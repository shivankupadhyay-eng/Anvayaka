from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from backend.models import Task

class Command(BaseCommand):
    help = 'Run MQTT listener for sensor data'

    def add_arguments(self, parser):
        parser.add_argument('--task_id', type=str, required=True, help='Task ID to update')

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()
        item_count = 0
        task_id = options['task_id']  # ✅ Get task id from argument
        task = Task.objects.get(id=task_id)
        if int(task.completed_quantity) == int(task.quantity):
            client.disconnect()
            return
        def on_connect(client, userdata, flags, rc):
            self.stdout.write(self.style.SUCCESS(f'Connected with result code {str(rc)}'))
            client.subscribe("emqx/esp32/temperature")
            client.subscribe("emqx/esp32/item")

        def on_message(client, userdata, msg):
            
            nonlocal item_count
            self.stdout.write(f"Received {msg.payload.decode()} from {msg.topic}")
            print(msg)
            print(task_id)
            try:
                if msg.topic == "emqx/esp32/temperature":
                    data = {'type': 'temperature', 'value': float(msg.payload.decode())}

                elif msg.topic == "emqx/esp32/item":
                    new_item_value = int(msg.payload.decode())
                    
                    if new_item_value:
                        item_count += new_item_value
                        data = {'type': 'item', 'value': item_count}
                        self.stdout.write(f"Total items counted: {item_count}")

                        # ✅ Update the correct Task dynamically
                        
                        task.completed_quantity += new_item_value
                        if int(task.completed_quantity) == int(task.quantity):
                            return
                        else:
                            task.save()
                        
                    else:
                        return

                async_to_sync(channel_layer.group_send)(
                    'sensor_data_group',
                    {'type': 'send_sensor_data', 'data': data}
                )

            except (ValueError, TypeError) as e:
                self.stdout.write(self.style.ERROR(f'Error processing message: {e}'))
            except Task.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Task {task_id} not found'))

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set("emqx", "public")

        try:
            client.connect("broker.emqx.io", 1883, 60)
            self.stdout.write(self.style.SUCCESS('Starting MQTT listener...'))
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('MQTT listener stopped'))
            client.disconnect()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'MQTT connection error: {e}'))
