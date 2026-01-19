"""
Helper functions and constants for City Voice application
"""

import pandas as pd
import os
import sys
from datetime import datetime
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db import get_connection

# Set up logging
logger = logging.getLogger(__name__)

# Zone Mapping for Bangalore Neighborhoods
ZONE_MAPPING = {
    "North": ["Hebbal", "Yelahanka", "RT Nagar", "Vidyaranyapura", "Sahakara Nagar", "Thanisandra"],
    "South": ["Jayanagar", "JP Nagar", "BTM Layout", "Banashankari", "HSR Layout", "Koramangala"],
    "East": ["Indiranagar", "Whitefield", "Marathahalli", "CV Raman Nagar", "Mahadevapura", "Varthur"],
    "West": ["Rajajinagar", "Malleshwaram", "Vijayanagar", "Basaveshwaranagar", "Kengeri", "Yeshwanthpur"]
}

# Available categories
CATEGORIES = ["Waste", "Water", "Traffic", "Electricity", "Sanitation", "Noise", "Other"]

# Get all areas from zone mapping
ALL_AREAS = []
for areas in ZONE_MAPPING.values():
    ALL_AREAS.extend(areas)
ALL_AREAS = sorted(ALL_AREAS)

# Zone authority mapping
ZONE_AUTHORITIES = {
    "North": {"password": "north_auth_123", "officer_name": "North Zone Authority"},
    "South": {"password": "south_auth_123", "officer_name": "South Zone Authority"},
    "East": {"password": "east_auth_123", "officer_name": "East Zone Authority"},
    "West": {"password": "west_auth_123", "officer_name": "West Zone Authority"},
    "Admin": {"password": "admin_123", "officer_name": "System Admin"}
}

def assign_zone(location):
    """Assign zone based on location"""
    location_normalized = location.strip().lower()
    for zone, neighborhoods in ZONE_MAPPING.items():
        for neighborhood in neighborhoods:
            if neighborhood.lower() == location_normalized:
                return zone
    return "Unknown"

def get_complaint_timeline(complaint_id):
    """Get timeline of actions for a complaint"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        query_complaint = "SELECT * FROM complaints WHERE complaint_id = %s"
        df_complaint = pd.read_sql(query_complaint, conn, params=(complaint_id,))
        
        if df_complaint.empty:
            return []
        
        complaint = df_complaint.iloc[0]
        timeline = []
        
        timeline.append({
            "date": complaint['created_at'],
            "status": "Submitted",
            "description": f"Complaint submitted by {complaint['citizen_name']}",
            "details": f"Category: {complaint['category']}, Priority: {complaint['priority']}",
            "image_path": None
        })
        
        query_logs = """
            SELECT * FROM action_log 
            WHERE complaint_id = %s 
            ORDER BY action_time ASC
        """
        df_logs = pd.read_sql(query_logs, conn, params=(complaint_id,))
        
        for _, log in df_logs.iterrows():
            timeline.append({
                "date": log['action_time'],
                "status": "Updated",
                "description": log['action'] if log['action'] else "Status updated",
                "details": f"Officer ID: {log['officer_id']}",
                "image_path": log.get('image_path') if 'image_path' in log else None
            })
        
        timeline.append({
            "date": datetime.now(),
            "status": complaint['status'],
            "description": f"Current Status: {complaint['status']}",
            "details": f"Zone: {complaint['zone']}",
            "image_path": None
        })
        
        return timeline
        
    except Exception as e:
        logger.error(f"Error fetching timeline: {str(e)}")
        return []
    finally:
        conn.close()

def fetch_complaints_by_zone(zone):
    """Fetch complaints by zone"""
    conn = get_connection()
    if conn:
        if zone == "Admin":
            query = "SELECT * FROM complaints ORDER BY priority DESC, created_at DESC"
        else:
            query = f"SELECT * FROM complaints WHERE zone = '{zone}' ORDER BY priority DESC, created_at DESC"
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

