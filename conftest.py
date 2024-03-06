import pytest
import os
import requests
import time

def pytest_addoption(parser):
  parser.addoption(
    '--target-env',
    action='store',
    default='prod',
    help='Environment name. eg: prod')
  
  parser.addoption(
      '--use-trained-model-id', 
        action='store', 
        default=None,
        help='provide existing trained model id')
  

@pytest.fixture(scope="session")  
def endpoint(request):
    env = request.config.getoption('--target-env')
    env_to_url = {
        "prod": "https://api.einstein.ai",

    }
    endpoint = env_to_url[env]
    return endpoint

@pytest.fixture(scope="session")  
def trained_model_id(request):
    model_id = request.config.getoption('--use-trained-model-id')
    return model_id

@pytest.fixture(scope="session")
def access_token(endpoint):
    refresh_token= os.environ['REFRESH_TOKEN']
    uri = "/v2/oauth2/token"
    test_endpoint = endpoint+uri
    payload = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "valid_for": 3600
    }
    response = requests.post(url=test_endpoint, data=payload)
    assert response.status_code == 200

    access_token = response.json()['access_token']
    return access_token

@pytest.fixture()
def model_dataset_id(endpoint,access_token):
    uri = "/v2/language/datasets/upload/sync"
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    payload={"type" : "text-intent"}
    files=[
        ('data',('weather.csv',open('weather.csv','rb'),'text/csv'))
    ]
    
    
    response = requests.post(url=test_endpoint, headers=headers, files=files, data=payload)
    assert response.status_code == 200 and response.json()["statusMsg"] == "SUCCEEDED", "Upload Dataset failed"
    model_dataset_id = response.json()["id"]
    return model_dataset_id

@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(3)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global failed
    report = yield
    result = report.get_result()

    if result.when == 'call' and result.outcome == "failed":
        failed = True
        print("FAILED")