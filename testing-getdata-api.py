import requests
import pandas as pd
import utilities as util

def authenticate_and_get_token():

    url = "https://pyten7y-dev1.build.ifs.cloud/auth/realms/pyten7ydev1/protocol/openid-connect/token"
    body = {
        "client_id":"IFS_connect",
        "client_secret":"CntEQOfknwA9OfxS8yNd",
        "username":"ifsapp",
        "password":"ifsapp",
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
    url = f"https://pyten7y-dev1.build.ifs.cloud/main/ifsapplications/projection/v1/CtmMetaDataHandling.svc/Reference_MetaData?$filter=TableName eq '{table_name}'"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers, verify=False)

    return response

def get_data(access_token, view_url):
    url = f"https://pyten7y-dev1.build.ifs.cloud/main/ifsapplications/projection/v1/{view_url}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers, verify=False)

    return response

def log_results(module, submodule, menu_name, table_name, response, summary, results_list):
    try:
        if pd.notnull(table_name):
            if response.status_code == 200:
                data = response.json()
                if data["value"]:
                    results_list.append({"Module": module, "Sub Module": submodule, "Menu Name": menu_name, 
                                "Table Name": table_name, "Status": "Passed", "Details": "WITH DATA"})
                    summary["Passed"] += 1
                else:
                    results_list.append({"Module": module, "Sub Module": submodule, "Menu Name": menu_name, 
                                "Table Name": table_name, "Status": "Passed", "Details": "EMPTY DATA"})
                    summary["Passed"] += 1
            else:
                error_response = response.json()
                results_list.append({"Module": module, "Sub Module": submodule, "Menu Name": menu_name, 
                                "Table Name": table_name, "Status": f"Failed", "Details": f"[{response.status_code}] - {error_response.get("error", {}).get("message")}"})
                summary["Failed"] += 1
        else:
            results_list.append({"Module": module, "Sub Module": submodule, "Menu Name": menu_name, 
                            "Table Name": "", "Status": f"Failed", "Details": f"VIEW NOT AVAILABLE"})
            summary["Failed"] += 1           
    except Exception as e:
        results_list.append({"Module": module, "Sub Module": submodule, "Menu Name": menu_name, 
                            "Table Name": table_name, "Status": "Failed", "Details": "OTHER PROJECTION ERROR"})
        summary["Failed"] += 1

def generate_ifs_projection(table_name_str):
    """Generate an IFS Projection from table_name."""
    if pd.notnull(table_name_str):
        pascal_str = util.snake_to_pascal(table_name_str)
        return f"{pascal_str}Handling.svc/{pascal_str}Set"
    else:
        return None


if __name__ == "__main__":
    df = pd.read_excel('Template API Unit Test.xlsx')
    # df = df.dropna().reset_index(drop=True).drop_duplicates(keep='first', ignore_index=True)
    # df = df.dropna().reset_index(drop=True)
    results_list = []  # Initialize an empty list to store result dictionaries

    access_token = authenticate_and_get_token()

    summary = {"Passed": 0, "Failed": 0}
    for index, row in df.iterrows():
        module = row['MODULE']
        submodule = row['SUBMODULE']
        menu_name = row['MENU NAMES']
        table_name = row['TABLE NAMES']
        view_url = row['SPECIFIC URL']
        if pd.notnull(table_name):
            if pd.isnull(view_url):
                view_url = generate_ifs_projection(table_name)
            else:
                view_url = view_url.replace("https://pyten7y-dev1.build.ifs.cloud/main/ifsapplications/projection/v1/", "")
            print(view_url)

            response = get_data(access_token, view_url)
            print(response.status_code)
            log_results(module, submodule, menu_name, table_name, response, summary, results_list)
        else:
            log_results(module, submodule, menu_name, table_name, None, summary, results_list)
    
    results_df = pd.DataFrame(results_list)  # Convert the list of dictionaries to a DataFrame

    # Adding summary at the end of DataFrame
    summary_df = pd.DataFrame([{"Table Name": "Summary", "Status": f"Passed: {summary['Passed']}, Failed: {summary['Failed']}"}])
    results_df = pd.concat([results_df, summary_df], ignore_index=True)
    
    # Writing results to an Excel file
    results_df.to_excel("api_test_results.xlsx", index=False)
