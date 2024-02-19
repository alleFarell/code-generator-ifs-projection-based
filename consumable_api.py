import requests

def authenticate_and_get_token():
    url = "https://csdkmi.ifssi.co.id/auth/realms/csdkmi/protocol/openid-connect/token"
    body = {
        "client_id": "surr_kmi",
        "client_secret": "NnVhf8bwr7d4Qs1b9BTlqCK0oPeXt0AW",
        "username": "ifsapp",
        "password": "ifsapp",
        "grant_type": "password",
        "scope": "openid",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(url, data=body, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"Error: {response.status_code}")
        return None

def get_meta_data(access_token, table_name):
    url = f"https://csdkmi.ifssi.co.id/main/ifsapplications/projection/v1/CtmMetaDataHandling.svc/Reference_GetMetaData?$filter=TableName eq '{table_name}'"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
access_token = authenticate_and_get_token()
if access_token:
    print("Successfully authenticated. Access token:", access_token)
    table_name = "CTM_PROD_MODEL"  # Dynamic parameter for table name
    data = get_meta_data(access_token, table_name)
    if data:
        print("Data received:", data)
else:
    print("Authentication failed.")
