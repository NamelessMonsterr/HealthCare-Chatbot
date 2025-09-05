import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict

class GovernmentHealthDataService:
    """Integrate with government health APIs and provide caching."""

    def __init__(self):
        self.mohfw_base_url = "https://api.mohfw.gov.in/v1"
        self.cowin_base_url = "https://cdn-api.co-vin.in/api/v2"
        
        self.mohfw_api_key = os.environ.get('MOHFW_API_KEY')
        self.cowin_api_key = os.environ.get('COWIN_API_KEY')
        
        self.cache = {}
        self.cache_timeout = 3600  # seconds
        
        self.headers = {
            'User-Agent': 'Healthcare-Chatbot/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        print("✅ Government health data service initialized")

    def get_cached_or_fetch(self, key: str, fetch_func, *args, **kwargs) -> Optional[Dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_timeout:
                print(f"📋 Using cached data for {key}")
                return data
        try:
            print(f"🔄 Fetching new data for {key}")
            data = fetch_func(*args, **kwargs)
            if data:
                self.cache[key] = (data, datetime.now())
            return data
        except Exception as e:
            print(f"❌ Data fetch error for {key}: {e}")
            return None

    def get_covid_statistics(self, state: str = None, district: str = None) -> Optional[Dict]:
        key = f"covid_stats_{state}_{district}"
        def fetch():
            # Mock data; replace with real API call to MOHFW with API key if available
            return self.get_mock_covid_data(state, district)
        return self.get_cached_or_fetch(key, fetch)

    def get_mock_covid_data(self, state: str = None, district: str = None) -> Dict:
        return {
            "data": {
                "state": state or "India",
                "district": district or "All Districts",
                "active_cases": 12345,
                "recovered": 1234567,
                "deaths": 123456,
                "vaccinated_dose1": 12345678,
                "vaccinated_dose2": 1234567,
                "last_updated": datetime.now().isoformat()
            },
            "status": "success",
            "message": "Sample COVID data"
        }

    def get_vaccination_centers(self, pincode: str, date: str = None) -> Optional[Dict]:
        if not date:
            date = datetime.now().strftime("%d-%m-%Y")
        key = f"vaccination_centers_{pincode}_{date}"
        def fetch():
            # Mock data; replace with real CoWIN API call
            return self.get_mock_vaccination_centers(pincode)
        return self.get_cached_or_fetch(key, fetch)

    def get_mock_vaccination_centers(self, pincode: str) -> Dict:
        return {
            "centers": [
                {
                    "center_id": 123456,
                    "name": f"Primary Health Center - {pincode}",
                    "address": f"Main Street, Pincode {pincode}",
                    "state_name": "Sample State",
                    "district_name": "Sample District",
                    "from": "09:00",
                    "to": "17:00",
                    "fee_type": "Free",
                    "sessions": [
                        {
                            "date": datetime.now().strftime("%d-%m-%Y"),
                            "available_capacity": 20,
                            "min_age_limit": 18,
                            "vaccine": "COVISHIELD",
                            "slots": ["09:00AM-11:00AM", "11:00AM-01:00PM"]
                        }
                    ]
                }
            ],
            "status": "success",
            "message": "Sample vaccination centers data"
        }

    # Additional APIs with mocks can be added here such as:
    # get_health_advisories, get_hospital_beds, get_medicine_info, etc.

# Global instance
health_data_service = GovernmentHealthDataService()

if __name__ == "__main__":
    print("🔧 Testing government health data service...")
    print(health_data_service.get_covid_statistics("Maharashtra", "Mumbai"))
    print(health_data_service.get_vaccination_centers("400001"))
    print("✅ Testing complete.")