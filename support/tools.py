
from orders.models import Order
from django.utils import timezone
# Creating tools to help the agent to do its work faster

# ------------------------
# Order Details as a tool
# ------------------------
def get_order_details(order_id):
    try:
        order = Order.objects.get(id = order_id)

        return{
            "order_id" : order.id,
            "product" : order.product_name,
            "amount" : str(order.amount),
            "status" : order.status,
            "carrier" : order.carrier,
            "tracking_number": order.tracking_number,
            "delivery_address": order.delivery,
            "ordered_on": order.created_at.strftime("%d %b %Y"), # 25 May 2026
            "days_since_order": (timezone.now() - order.created_at).days,
        }
    except Order.DoesNotExist:
        return {"error": f"Order #{order_id} is not found."}
    

# ------------------------
# Order Details as a tool
# ------------------------
