from langchain.tools import tool
from .tools import (
       get_order_details as order_details,
       get_refund_history as refund_history,
       check_delivery_status as check_delivery,
       search_knowledge_base as search_knowledge
    )

@tool
def get_order_details(order_id: int) -> dict:
    """Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery"""
    return order_details(order_id)


@tool
def get_refund_history(user_id: int) -> dict:
    """Get complete refund history for a user. Use this before making any refund related decisions."""
    return refund_history(user_id)


@tool
def check_delivery_status(tracking_number: str, carrier: str) -> dict:
    """Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery."""
    return check_delivery(tracking_number,carrier)
    

@tool
def search_knowledge_base(query: str) -> dict:
    """Search CoolBreze AC documents including refund policy, warranty policy and product FAQs. Use this this when customer ask about company policies, warrant coverage, warranty claims, refund eligibility, or  any general product information"""
    return search_knowledge(query)
