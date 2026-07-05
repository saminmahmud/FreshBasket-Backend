import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order, OrderLiveLocation

class OrderLiveLocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]

        self.room_group_name = f"order_{self.order_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
        # print(f"Connected to order {self.order_id} live location channel.")
 
    
    async def disconnect(self, close_code):
        try:
            await self.mark_offline()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "location_offline",
                }
            )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

        except Exception as e:
            import traceback
            traceback.print_exc()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
    
    
    @database_sync_to_async
    def mark_offline(self):
        try:
            order = Order.objects.get(id=self.order_id)

            if hasattr(order, "live_location"):
                order.live_location.delete()

        except Order.DoesNotExist:
            pass
    
    
    async def location_offline(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "offline": True
                }
            )
        )


    async def receive(self, text_data):
        data = json.loads(text_data)

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return
        
        if latitude is None or longitude is None:
            return

        await self.save_location(
            latitude,
            longitude,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "location_update",
                "latitude": latitude,
                "longitude": longitude,
            },
        )

    async def location_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "latitude": event["latitude"],
                    "longitude": event["longitude"],
                }
            )
        )


    @database_sync_to_async
    def save_location(self, latitude, longitude):
        try:
            order = Order.objects.select_related("delivery_partner").get(id=self.order_id)
        except Order.DoesNotExist:
            return

        OrderLiveLocation.objects.update_or_create(
            order=order,
            defaults={
                "delivery_partner": order.delivery_partner,
                "latitude": latitude,
                "longitude": longitude,
            },
        )