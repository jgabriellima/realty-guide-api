import requests

BASE_URL = "http://localhost:8080"


def property_lookup(url):
    response = requests.post(f"{BASE_URL}/property_lookup", json={"url": url})
    return response.json()


def enrich_property_data(property_id):
    response = requests.post(f"{BASE_URL}/enrich_property_data", json={"property_id": property_id})
    return response.json()


def client_profile_lookup(client_id):
    response = requests.post(f"{BASE_URL}/client_profile_lookup", json={"client_id": client_id})
    return response.json()


def get_enrichment_data(property_id, data_type):
    response = requests.post(f"{BASE_URL}/get_enrichment_data",
                             json={"property_id": property_id, "data_type": data_type})
    return response.json()


def save_client_preferences(client_id, preferences):
    response = requests.post(f"{BASE_URL}/save_client_preferences",
                             json={"client_id": client_id, "preferences": preferences})
    return response.json()


def get_customized_recommendations(property_id, client_id):
    response = requests.post(f"{BASE_URL}/get_customized_recommendations",
                             json={"property_id": property_id, "client_id": client_id})
    return response.json()


def store_agent_data(agent_id, interaction_data):
    response = requests.post(f"{BASE_URL}/store_agent_data",
                             json={"agent_id": agent_id, "interaction_data": interaction_data})
    return response.json()


def retrieve_agent_data(agent_id):
    response = requests.post(f"{BASE_URL}/retrieve_agent_data", json={"agent_id": agent_id})
    return response.json()


# Example usage:
if __name__ == "__main__":
    # Property Lookup
    property_info = property_lookup("http://example.com/property/123")
    print("Property Info:", property_info)

    # Enrich Property Data
    enriched_data = enrich_property_data(property_info['property_id'])
    print("Enriched Data:", enriched_data)

    # Client Profile Lookup
    client_info = client_profile_lookup("456")
    print("Client Info:", client_info)

    # Get Enrichment Data for Schools
    school_data = get_enrichment_data(property_info['property_id'], "schools")
    print("School Data:", school_data)

    # Save Client Preferences
    preferences = {"children": True, "commute": "city center"}
    save_status = save_client_preferences("456", preferences)
    print("Save Preferences Status:", save_status)

    # Get Customized Recommendations
    recommendations = get_customized_recommendations(property_info['property_id'], "456")
    print("Recommendations:", recommendations)

    # Store Agent Data
    interaction_data = {"client": "John Doe", "property": "123 Main St",
                        "details": "Discussed school ratings and traffic conditions."}
    store_status = store_agent_data("789", interaction_data)
    print("Store Data Status:", store_status)

    # Retrieve Agent Data
    last_interaction = retrieve_agent_data("789")
    print("Last Interaction Data:", last_interaction)
