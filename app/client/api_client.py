import requests


class RealtyGuideClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def property_lookup(self, url, real_estate_agent_id):
        endpoint = f"{self.base_url}/v1/properties/lookup"
        payload = {
            "url": url,
            "real_estate_agent_id": real_estate_agent_id
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def enrich_property_data(self, property_slug, request_details, real_estate_agent_id):
        endpoint = f"{self.base_url}/v1/properties/enrich_property_data"
        payload = {
            "property_slug": property_slug,
            "request_details": request_details,
            "real_estate_agent_id": real_estate_agent_id
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def client_lookup(self, whatsapp_number):
        endpoint = f"{self.base_url}/v1/clients/client_lookup"
        payload = {
            "whatsapp_number": whatsapp_number
        }
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    def save_client_memory_preferences(self, whatsapp_number, parameter_name, parameter_value_description):
        endpoint = f"{self.base_url}/v1/clients/save_client_memory_preferences"
        payload = {
            "whatsapp_number": whatsapp_number,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def save_agent_memory_preferences(self, whatsapp_number, parameter_name, parameter_value_description):
        endpoint = f"{self.base_url}/v1/agents/save_agent_memory_preferences"
        payload = {
            "whatsapp_number": whatsapp_number,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def agent_lookup(self, whatsapp_number):
        endpoint = f"{self.base_url}/v1/agents/agent_lookup"
        payload = {
            "whatsapp_number": whatsapp_number
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def schedule_remainder(self, real_estate_agent_id, remainder_description, remainder_time_in_seconds):
        endpoint = f"{self.base_url}/v1/agents/schedule_remainder"
        payload = {
            "real_estate_agent_id": real_estate_agent_id,
            "remainder_description": remainder_description,
            "remainder_time_in_seconds": remainder_time_in_seconds
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def check_task_status(self, task_id):
        endpoint = f"{self.base_url}/v1/taskscheck_task_status"
        payload = {
            "task_id": task_id
        }
        response = requests.post(endpoint, json=payload)
        return response.json()

    def root(self):
        endpoint = f"{self.base_url}/"
        response = requests.get(endpoint)
        return response.json()


# Exemplo de uso do cliente
if __name__ == "__main__":
    # client = RealtyGuideClient(base_url="https://realty-guide-api-production.up.railway.app")
    client = RealtyGuideClient(base_url="http://localhost:8000")
    real_estate_agent_id = 1
    # property: Property = parse_to_schema(Property, [client.property_lookup(url="https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569", real_estate_agent_id=real_estate_agent_id)])
    # print(f"Property: {property}")

    # # Exemplo de Enrich Property Data
    # property = client.enrich_property_data(property_slug=property.slug, request_details="Quais as escolas proximas dessa imóvel?", real_estate_agent_id=1)
    # print(f"Property enriched: {property}")

    # # Exemplo de Client Lookup
    print(client.client_lookup(whatsapp_number="48991302288"))
    #
    # # Exemplo de Save Client Memory Preferences
    # print(client.save_client_memory_preferences(whatsapp_number="123456789", parameter_name="name",
    #                                             parameter_value_description="description"))
    #
    # # Exemplo de Save Agent Memory Preferences
    # print(client.save_agent_memory_preferences(whatsapp_number="123456789", parameter_name="name",
    #                                            parameter_value_description="description"))
    #
    # # Exemplo de Agent Lookup
    # print(client.agent_lookup(whatsapp_number="123456789"))
    #
    # # Exemplo de Schedule Remainder
    # print(client.schedule_remainder(real_estate_agent_id=1, remainder_description={"task": "Follow up"},
    #                                 remainder_time_in_seconds=3600))
    #
    # # Exemplo de Check Task Status
    # print(client.check_task_status(task_id="task-id"))
    #
    # # Exemplo de Root
    # print(client.root())
