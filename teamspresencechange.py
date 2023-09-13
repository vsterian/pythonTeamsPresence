import requests
import webbrowser
import logging
import msal
import json
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.subscriptions.subscriptions_request_builder import SubscriptionsRequestBuilder
import asyncio
from msgraph import GraphRequestAdapter

from msgraph.generated.models.subscription import Subscription
from datetime import datetime, timedelta





logging.basicConfig(level=logging.INFO)

# Azure AD App credentials
client_id = '4013e8bf-7904-421c-8c8b-5f32441edff6'
tenant_id = '1f97ae5f-b765-4494-a8a4-5b0955d6673a'
authority = f'https://login.microsoftonline.com/{tenant_id}'
client_secret ='5xs8Q~kJUuMVGpKmYib5NfMNA_iYqIcObrIOrapw'
scopes = ['https://graph.microsoft.com/.default']

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

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret)


request_adapter = GraphRequestAdapter(auth_provider=authority)
graph_client = GraphServiceClient(credential, scopes)

if "access_token" in result:
    access_token = result['access_token']
    logging.info(f"Access token retrieved: {access_token}")
    
    # Define the subscription payload
    
    
expiration_time = datetime.utcnow() + timedelta(minutes=58)
expiration_time_str = expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    
async def create_subscription():

        
        subscription_data = Subscription(
        change_type = "updated",
        notification_url = "https://wildteamspresence1.azurewebsites.net/api/presenceNotification?code=umn1zuc1CkeJutJCf1qoK5J0MdfBxx1obJjTM0zC8s80AzFuSxPtEQ==",
        resource =  f"/communications/presences/{user_id}",
        expiration_date_time = "2023-09-13T12:30:45",
        #client_state = None,
       
)
        
        subscription_data.expirationDateTime = expiration_time_str 
        
        try:
            
            
            
            # Create the subscription using the GraphServiceClient
            logging.info("Creating the subscription...")
            

            created_subscription = await graph_client.subscriptions.post(body= subscription_data)
            print("Subscription to presence changes created successfully.")
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))  # You might need this when reporting a bug.
if __name__=="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_subscription())
