"""
title: FDA Drug Information Tools
author: open-webui
description: Access FDA drug shortages, recalls, and medication information via MCP server
version: 1.0.0
"""

import json
import requests
import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class Tools:
    class Valves(BaseModel):
        MCP_SERVER_URL: str = Field(
            default=os.getenv("MCP_SERVER_URL", "https://certus.opensource.mieweb.org/mcp"),
            description="Your MCP server URL"
        )
        TIMEOUT: int = Field(default=10, description="Request timeout in seconds")

    def __init__(self):
        self.valves = self.Valves()

    def search_drug_shortages(self, drug_name: str, limit: int = 5) -> str:
        """Search for current drug shortages using FDA data."""
        try:
            print(f"🔍 Searching drug shortages for: {drug_name}")
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/tools/search_drug_shortages",
                json={"drug_name": drug_name, "limit": limit},
                timeout=self.valves.TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return f"❌ Error: MCP server returned status {response.status_code}"
            
            data = response.json()
            
            if not data:
                return f"No shortage data found for {drug_name}"
            
            # Format the response nicely
            summary = f"📊 **Drug Shortage Information for {drug_name.title()}**\n\n"
            
            if 'results' in data and data['results']:
                results = data['results'][:limit]
                for i, shortage in enumerate(results, 1):
                    summary += f"**{i}. {shortage.get('product_description', 'Unknown Product')}**\n"
                    summary += f"   • Status: {shortage.get('shortage_status', 'Unknown')}\n"
                    if shortage.get('reason'):
                        summary += f"   • Reason: {shortage.get('reason')}\n"
                    summary += "\n"
            else:
                summary += f"✅ No current shortages reported for {drug_name}"
            
            return summary
            
        except Exception as e:
            return f"❌ Error searching drug shortages: {str(e)}"

    def get_medication_profile(self, drug_name: str) -> str:
        """Get complete medication profile including FDA label information."""
        try:
            print(f"📋 Getting medication profile for: {drug_name}")
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/tools/get_medication_profile",
                json={"drug_identifier": drug_name},
                timeout=self.valves.TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return f"❌ Error: MCP server returned status {response.status_code}"
            
            data = response.json()
            profile = f"💊 **Medication Profile: {drug_name.title()}**\n\n"
            
            if 'label_info' in data and data['label_info']:
                label = data['label_info'][0] if isinstance(data['label_info'], list) else data['label_info']
                
                if 'openfda' in label:
                    openfda = label['openfda']
                    if 'brand_name' in openfda:
                        profile += f"**Brand Name(s):** {', '.join(openfda['brand_name'])}\n"
                    if 'generic_name' in openfda:
                        profile += f"**Generic Name(s):** {', '.join(openfda['generic_name'])}\n"
                    if 'manufacturer_name' in openfda:
                        profile += f"**Manufacturer(s):** {', '.join(openfda['manufacturer_name'])}\n"
                
                if 'indications_and_usage' in label:
                    profile += f"\n**Indications:** {label['indications_and_usage'][0][:300]}...\n"
            
            return profile
            
        except Exception as e:
            return f"❌ Error getting medication profile: {str(e)}"

    def search_drug_recalls(self, drug_name: str, limit: int = 3) -> str:
        """Search for drug recalls and safety alerts."""
        try:
            print(f"⚠️ Searching drug recalls for: {drug_name}")
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/tools/search_drug_recalls",
                json={"drug_name": drug_name, "limit": limit},
                timeout=self.valves.TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return f"❌ Error: MCP server returned status {response.status_code}"
            
            data = response.json()
            
            if not data or 'results' not in data or not data['results']:
                return f"✅ No recalls found for {drug_name}"
            
            results = data['results'][:limit]
            summary = f"⚠️ **Drug Recall Information for {drug_name.title()}**\n\n"
            
            for i, recall in enumerate(results, 1):
                summary += f"**{i}. {recall.get('product_description', 'Unknown Product')}**\n"
                summary += f"   • Recall Date: {recall.get('recall_initiation_date', 'Unknown')}\n"
                summary += f"   • Reason: {recall.get('reason_for_recall', 'Not specified')}\n"
                summary += f"   • Classification: {recall.get('classification', 'Unknown')}\n\n"
            
            return summary
            
        except Exception as e:
            return f"❌ Error searching drug recalls: {str(e)}"
