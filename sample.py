import msal
import requests
import json
import os

# Azure AD App credentials
client_id = '4013e8bf-7904-421c-8c8b-5f32441edff6'
tenant_id = '1f97ae5f-b765-4494-a8a4-5b0955d6673a'
authority = f'https://login.microsoftonline.com/{tenant_id}'

# MS Teams user id
user_id = '1ecbd423-b0cc-4955-925a-589859e8d58b'

# Create a preferably long-lived app instance which maintains a token cache.
app = msal.PublicClientApplication(
    client_id, authority=authority,
)

# The pattern to acquire a token looks like this.
result = None

# First, the code looks up a token from the cache.
accounts = app.get_accounts()
if accounts:
    result = app.acquire_token_silent(["Presence.Read.All"], account=accounts[0])

if not result:
    # It's possible we have no accounts in the token cache, or no tokens for those accounts.
    # Let's get a new one from AAD.
    flow = app.initiate_device_flow(scopes=["Presence.Read.All"])
    if "user_code" not in flow:
        raise ValueError(
            "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
    
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)  # By default it will block

if "access_token" in result:
    # Call a protected API with the access token.
    headers = {'Authorization': 'Bearer ' + result['access_token']}
    
    
   
    
    # Create a subscription to presence changes
    subscription_data = {
        "changeType": "updated",
        "notificationUrl": "https://wildteamspresence1.azurewebsites.net/api/presenceNotification?code=umn1zuc1CkeJutJCf1qoK5J0MdfBxx1obJjTM0zC8s80AzFuSxPtEQ==",
     
       
        "resource": f"/communications/presences/{user_id}",
        "expirationDateTime":"2023-09-12T18:23:45.9356913Z",
      
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
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You might need this when reporting a bug.
