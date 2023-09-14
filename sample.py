import requests
import json
import os
import threading
from azure.identity import InteractiveBrowserCredential
from datetime import datetime, timedelta

# Azure AD App credentials
client_id = '09be529a-eedd-46f5-8af4-be2d7332c552'
tenant_id = '72f988bf-86f1-41af-91ab-2d7cd011db47'

# MS Teams user id
user_id = '6e65cc58-12fb-4c0d-befa-147fe89270c9'

# Create an instance of InteractiveBrowserCredential
credential = InteractiveBrowserCredential(client_id=client_id, tenant_id=tenant_id, redirect_uri='http://localhost:8000')

expiration_time = datetime.utcnow() + timedelta(minutes=58)
expiration_time_str = expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def renew_subscription():
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
            "expirationDateTime":expiration_time_str,
        }

        response = requests.post(
            'https://graph.microsoft.com/beta/subscriptions',
            headers=headers,
            json=subscription_data
        )

        if response.status_code == 201:
            print("Subscription renewed successfully.")
        elif response.status_code == 409:
            print("A subscription already exists. It must be deleted before another can be made.")

        else:
            print(f"Failed to renew subscription. Status code: {response.status_code}. Message: {response.text}")
    else:
        print("Failed to acquire token.")

    # Schedule the next renewal
    threading.Timer(60 * 60, renew_subscription).start()

# Start the first renewal
renew_subscription()
