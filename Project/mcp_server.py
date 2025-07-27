'''
import os
import django
from mcp.server.fastmcp import FastMCP
import json
from mcp.server.fastmcp import FastMCP
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Project.settings")
django.setup()
from Client.models import CustomUser
from Complaint.models import Complaints
''''''
# uv run mcp install mcp_server.py
#pip install mcp[cli],mcp,uv
#uv run mcp install mcp_server.py

# Set up Django environment
User=get_user_model()
mcp = FastMCP("User & Complaint Assistant")

# Tool 1: Get user info
@mcp.tool()
def get_user_info(user_id: int) -> dict:
    """Fetch user information by user ID."""
    try:
        """ 
         data = {
            field.name: getattr(user, field.name)
            for field in user._meta.fields/meta.get_fields
        }
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return {"user": json_data}
        """
        user = CustomUser.objects.get(id=user_id)
        return model_to_dict(user)
    
    except CustomUser.DoesNotExist:
        return {"error": "User not found."}

# Tool 2: Get complaint status
@mcp.tool()
def get_complaint_status(complaint_id: str) -> dict:
    """Get the status of a complaint."""
    try:
        complaint = Complaints.objects.get(complaint_id=complaint_id)
        return model_to_dict(complaint)
    except Complaints.DoesNotExist:
        return {"error": "Complaint not found."}

# ──────────────────────────────────────────────
# 💬 Chat Handler: Handle Chat Messages
# ──────────────────────────────────────────────
@mcp.chat()
def handle_user_message(message: str) -> str:
    """
    Respond to user messages.
    This is a simple rule-based handler. You can make it smarter with tool calls.
    """
    message = message.lower()

    if "name" in message or "who am i" in message:
        return "To see your profile, type: 'Get my user info'"

    elif "status" in message or "ticket" in message or "complaint" in message:
        return "To check complaint status, say: 'Check complaint status <complaint_id>'"

    return (
        "I'm here to help!\n"
        "Try asking:\n"
        "🟢 'What is my profile?'\n"
        "🟢 'Check complaint status CMP12345'"
    )

'''

'''
if __name__ == "__main__":
    mcp.run()
'''