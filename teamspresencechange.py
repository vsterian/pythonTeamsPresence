import requests
import webbrowser
import logging
import msal
import json

logging.basicConfig(level=logging.INFO)

# Azure AD App credentials
client_id = '4013e8bf-7904-421c-8c8b-5f32441edff6'
tenant_id = '1f97ae5f-b765-4494-a8a4-5b0955d6673a'
authority = f'https://login.microsoftonline.com/{tenant_id}'

# MS Teams user id
user_id = '1ecbd423-b0cc-4955-925a-589859e8d58b'

app = msal.PublicClientApplication(
    client_id, authority=authority,
)
result = None


accounts = app.get_accounts()
if accounts:
    result = app.acquire_token_silent(["Presence.Read.All"], account=accounts[0])

if not result:
    flow = app.initiate_device_flow(scopes=["Presence.Read.All"])
    if "user_code" not in flow:
        raise ValueError(
            "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

    print(flow["message"])
    webbrowser.open(flow["verification_uri"])  # Open the verification_uri in the default web browser
    result = app.acquire_token_by_device_flow(flow)  # By default, it will block until the user completes the flow

if "access_token" in result:

    access_token = result['access_token']
    logging.info(f"Access token retrieved: {access_token}")
    
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    
   #This part down , does not work. It seems like you need to pass some additional certificates for this presence change 

    # Define the subscription payload
    subscription_data = {
        "changeType": "updated",
        "notificationUrl": "https://wildteamspresence1.azurewebsites.net/api/presenceNotification?code=umn1zuc1CkeJutJCf1qoK5J0MdfBxx1obJjTM0zC8s80AzFuSxPtEQ==",
     
        "includeResourceData": "true",
        "resource": f"/communications/presences/{user_id}",
        "expirationDateTime":"2023-09-12T18:23:45.9356913Z",
      
    }

    subscription_url = "https://graph.microsoft.com/v1.0/subscriptions"

    try:
        # Create the subscription using the access token
        logging.info("Creating the subscription...")
        create_subscription_response = requests.post(subscription_url, headers=headers, json=subscription_data)
        create_subscription_response.raise_for_status()
        print("Subscription to presence changes created successfully.")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Response content: {create_subscription_response.content}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You might need this when reporting a bug.
