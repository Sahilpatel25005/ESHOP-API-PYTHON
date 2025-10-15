from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    # **Contract**: frontend must send amount in *major* currency units
    # Example: for INR ₹2000 -> send 2000. For USD $20 -> send 20.
    promocode : str