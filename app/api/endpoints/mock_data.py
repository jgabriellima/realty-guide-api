# Mock data for demonstration purposes
mock_property_data = {
    "123": {
        "address": "123 Main St",
        "price": 300000,
        "area": "2000 sqft"
    }
}

mock_enriched_data = {
    "123": {
        "schools": [
            {"name": "Springfield Elementary", "rating": 4.5, "distance": "0.5 miles"},
            {"name": "Shelbyville High", "rating": 4.0, "distance": "1 mile"}
        ],
        "traffic": {
            "peak_hours": ["7am-9am", "5pm-7pm"],
            "current_conditions": "Moderate"
        },
        "supermarkets": [
            {"name": "Fresh Mart", "distance": "0.3 miles"},
            {"name": "Super Saver", "distance": "0.7 miles"}
        ],
        "hospitals": [
            {"name": "City Hospital", "distance": "1.2 miles"},
            {"name": "County General", "distance": "2 miles"}
        ],
        "maternity_centers": [
            {"name": "Mother Care", "distance": "1.5 miles"},
            {"name": "Baby Center", "distance": "2.2 miles"}
        ]
    }
}

mock_client_profiles = {
    "456": {
        "name": "John Doe",
        "preferences": {
            "children": True,
            "commute": "city center"
        }
    }
}

mock_agent_data = {
    "789": {
        "last_interaction": {
            "client": "John Doe",
            "property": "123 Main St",
            "details": "Discussed school ratings and traffic conditions."
        }
    }
}

mock_client_preferences = {
    "456": {
        "children": True,
        "commute": "city center"
    }
}

mock_property_metadata = {
    "123": {
        "extra_info": "Beautiful garden and spacious backyard."
    }
}
