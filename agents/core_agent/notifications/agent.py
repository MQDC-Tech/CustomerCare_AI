"""Notifications Agent for handling alerts and communication."""

from google.adk import Agent
from google.adk.tools import FunctionTool
from typing import Dict, Any, List
from datetime import datetime
import json


def send_notification(recipient: str, message: str, channel: str = "email", priority: str = "normal") -> Dict[str, Any]:
    """
    Send a notification to a recipient.
    
    Args:
        recipient: Recipient identifier (email, phone, user_id)
        message: Notification message
        channel: Communication channel (email, sms, push, slack)
        priority: Priority level (low, normal, high, urgent)
        
    Returns:
        Notification sending result
    """
    notification = {
        "id": f"notif_{datetime.now().timestamp()}",
        "recipient": recipient,
        "message": message,
        "channel": channel,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }
    
    return {
        "notification_id": notification["id"],
        "status": "sent",
        "message": f"Notification sent to {recipient} via {channel}"
    }


def schedule_notification(recipient: str, message: str, schedule_time: str, channel: str = "email") -> Dict[str, Any]:
    """
    Schedule a notification for later delivery.
    
    Args:
        recipient: Recipient identifier
        message: Notification message
        schedule_time: ISO format timestamp for delivery
        channel: Communication channel
        
    Returns:
        Scheduling confirmation
    """
    return {
        "notification_id": f"scheduled_{datetime.now().timestamp()}",
        "status": "scheduled",
        "delivery_time": schedule_time,
        "message": f"Notification scheduled for {recipient} at {schedule_time}"
    }


def get_notification_status(notification_id: str) -> Dict[str, Any]:
    """
    Get the status of a notification.
    
    Args:
        notification_id: Notification identifier
        
    Returns:
        Notification status information
    """
    return {
        "notification_id": notification_id,
        "status": "delivered",
        "delivery_time": datetime.now().isoformat(),
        "read_status": "unread"
    }


def send_alert(alert_type: str, message: str, severity: str = "medium") -> Dict[str, Any]:
    """
    Send system alerts to administrators.
    
    Args:
        alert_type: Type of alert (error, warning, info, security)
        message: Alert message
        severity: Alert severity (low, medium, high, critical)
        
    Returns:
        Alert sending result
    """
    alert = {
        "id": f"alert_{datetime.now().timestamp()}",
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "alert_id": alert["id"],
        "status": "sent",
        "message": f"{severity.upper()} {alert_type} alert sent to administrators"
    }


# Create the notifications agent
root_agent = Agent(
    name="notifications",
    model="gemini-1.5-flash",
    tools=[
        FunctionTool(send_notification),
        FunctionTool(schedule_notification),
        FunctionTool(get_notification_status),
        FunctionTool(send_alert)
    ],
    instruction="""
    You are the Notifications Agent responsible for:
    1. Sending notifications via various channels (email, SMS, push, Slack)
    2. Scheduling notifications for future delivery
    3. Managing notification status and delivery tracking
    4. Sending system alerts and warnings
    
    Ensure timely and reliable communication delivery.
    """
)
