
from orders.models import Order,RefundRequest
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
# Refund History as a tool
# ------------------------
def get_refund_history(user_id):
    refunds = RefundRequest.objects.filter(user_id=user_id).order_by("-created_at")

    history = []

    for refund in refunds:
        history.append({
            "order_id" : refund.order.id,
            "product" : refund.order.product_name,
            "reason" : refund.reason,
            "status" : refund.status,
            "requested_on" : refund.created_at.strftime("%d %b %Y"),

        })

    return{
        "total_refund_request" : len(history),
        "history":history
    }

