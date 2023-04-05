import requests
import json
from kubernetes import client, config

# Prisma Cloud Compute Console configuration
url = 'https://<your-console-url>:<port>'
username = '<your-username>'
password = '<your-password>'

# Kubernetes configuration
namespace = 'default'  # Replace with the namespace where the webhook is deployed
webhook_deployment_name = 'admission-webhook'  # Replace with the actual webhook deployment name

def login_to_console(url, username, password):
    login_url = f'{url}/api/v1/authenticate'
    credentials = {'username': username, 'password': password}
    response = requests.post(login_url, json=credentials)

    if response.status_code == 200:
        return response.json().get('token')
    else:
        print("Failed to log in to the console")
        return None

def get_admission_control_status(url, token):
    headers = {'Authorization': f'Bearer {token}'}
    admission_control_url = f'{url}/api/v1/defenders'
    response = requests.get(admission_control_url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if 'admission_control' in result:
            return result['admission_control']['enabled']
        else:
            print("Admission control data not found")
            return None
    else:
        print("Failed to retrieve admission control status")
        return None

def load_kube_config():
    try:
        config.load_kube_config()
        return True
    except Exception as e:
        print(f"Error loading Kubernetes configuration: {e}")
        return False

def check_webhook_deployment():
    api_instance = client.AppsV1Api()

    try:
        deployment = api_instance.read_namespaced_deployment(
            name=webhook_deployment_name,
            namespace=namespace
        )
        if deployment:
            print(f"Webhook deployment '{webhook_deployment_name}' found in the '{namespace}' namespace.")
            return True
        else:
            print(f"Webhook deployment '{webhook_deployment_name}' not found in the '{namespace}' namespace.")
            return False
    except client.rest.ApiException as e:
        if e.status == 404:
            print(f"Webhook deployment '{webhook_deployment_name}' not found in the '{namespace}' namespace.")
        else:
            print(f"Error checking webhook deployment: {e}")
        return False

def main():
    token = login_to_console(url, username, password)
    if token:
        admission_control_status = get_admission_control_status(url, token)
        if admission_control_status is not None:
            print(f"Admission control feature is {'enabled' if admission_control_status else 'disabled'}")

    if load_kube_config():
        check_webhook_deployment()

if __name__ == '__main__':
    main()
