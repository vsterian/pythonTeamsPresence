import requests
import json
import os
from azure.identity import InteractiveBrowserCredential

# Azure AD App credentials
client_id = '09be529a-eedd-46f5-8af4-be2d7332c552'
tenant_id = '72f988bf-86f1-41af-91ab-2d7cd011db47'


# MS Teams user id
user_id = '6e65cc58-12fb-4c0d-befa-147fe89270c9'

# Create an instance of InteractiveBrowserCredential
credential = InteractiveBrowserCredential(client_id=client_id, tenant_id=tenant_id, redirect_uri='http://localhost:8000')

# Get a token for the Graph API scope
token = credential.get_token('Presence.Read.All')

if token:
    # Call a protected API with the access token.
    headers = {'Authorization': 'Bearer ' + token.token}

    # Create a subscription to presence changes
    subscription_data = {
        "changeType": "updated",
        "notificationUrl": "https://wildteamspresence1.azurewebsites.net/api/presenceNotification?code=umn1zuc1CkeJutJCf1qoK5J0MdfBxx1obJjTM0zC8s80AzFuSxPtEQ==",
        "resource": f"/communications/presences/{user_id}",
        "expirationDateTime":"2023-09-13T15:23:45.9356913Z",
    }

    response = requests.post(
        'https://graph.microsoft.com/beta/subscriptions',
        headers=headers,
        json=subscription_data
    )

    if response.status_code == 201:
        print("Subscription created successfully.")
    else:
        print(f"Failed to create subscription. Status code: {response.status_code}. Message: {response.text}")
else:
    print("Failed to acquire token.")
