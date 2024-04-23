import requests
import pandas as pd

def authenticate_and_get_token():
    # url = "https://ifscloud.ifssi.co.id/auth/realms/isidev/protocol/openid-connect/token"
    # body = {
    #     "client_id":"STO",
    #     "client_secret":"FjvbcDWtNgf6Oo7kCGUyDHHeZGgKBPro",
    #     "username":"ifsapp",
    #     "password":"ifsapp",
    #     "grant_type":"password",
    #     "scope":"openid",
    #     "response_type":"id_token"
    # }

    url = "https://pyten7y-dev2.build.ifs.cloud/auth/realms/pyten7ydev2/protocol/openid-connect/token"
    body = {
        "client_id": "IFS_connect",
		"client_secret": "kGHGIieCMOLYX2NyIvz8",
		"username":"ifsapp",
		"password":"8tc9CIWgwLI7aOa7Jl1CFtlOLrO6Bz",
		"grant_type":"password",
		"scope":"openid",
		"response_type":"id_token"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(url, data=body, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"Error GET TOKEN: {response.status_code}")
        return None

def get_meta_data(access_token, table_name):
    url = f"https://ifscloud.ifssi.co.id/main/ifsapplications/projection/v1/CtmMetaDataHandling.svc/Reference_GetMetaData?$filter=TableName eq '{table_name}'"
    # url = f"https://pyten7y-dev2.build.ifs.cloud/main/ifsapplications/projection/v1/CtmMetaDataHandling.svc/Reference_MetaData?$filter=TableName eq '{table_name}'"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers, verify=False)

    return response

def log_results(table_name, response, summary, results_list):
    try:
        if response.status_code == 200:
            data = response.json()
            if data["value"]:
                results_list.append({"Table Name": table_name, "Status": "Passed"})
                summary["Passed"] += 1
            else:
                results_list.append({"Table Name": table_name, "Status": "Failed - EMPTY RESPONSE"})
                summary["Failed"] += 1
        else:
            results_list.append({"Table Name": table_name, "Status": f"Failed - Status Code: {response.status_code}"})
            summary["Failed"] += 1
    except Exception as e:
        results_list.append({"Table Name": table_name, "Status": "Failed - PROJECTION ERROR"})
        summary["Failed"] += 1

if __name__ == "__main__":
    df = pd.read_excel('API Unit Test.xlsx')
    df = df.dropna().reset_index(drop=True).drop_duplicates(keep='first', ignore_index=True)

    results_list = []  # Initialize an empty list to store result dictionaries

    access_token = authenticate_and_get_token()

    summary = {"Passed": 0, "Failed": 0}
    for table_name in df['TABLE NAMES']:
        response = get_meta_data(access_token, table_name)
        log_results(table_name, response, summary, results_list)
    
    results_df = pd.DataFrame(results_list)  # Convert the list of dictionaries to a DataFrame

    # Adding summary at the end of DataFrame
    summary_df = pd.DataFrame([{"Table Name": "Summary", "Status": f"Passed: {summary['Passed']}, Failed: {summary['Failed']}"}])
    results_df = pd.concat([results_df, summary_df], ignore_index=True)
    
    # Writing results to an Excel file
    results_df.to_excel("api_test_results.xlsx", index=False)
