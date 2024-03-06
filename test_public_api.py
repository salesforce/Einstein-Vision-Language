
import requests
import logging
import pytest
import os

logger = logging.getLogger()

def test_get_api_usage(access_token,endpoint):
    logger.info("Starting test for %s",endpoint)
    uri = "/v2/apiusage"
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Get API Usage failed"
    logger.info(response.text)

def test_upload_dataset(access_token,endpoint,request):
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
    assert response.status_code == 200, "Upload Dataset failed"
    logger.info("upload_dataset result:{}".format(response.text))
    dataset_id = response.json()["id"]
    request.config.cache.set('dataset_id', dataset_id)

def test_update_dataset(access_token,endpoint,request):
    dataset_id = request.config.cache.get('dataset_id', None)
    uri = "/v2/language/datasets/{}/upload".format(dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    
    payload={}
    files=[
        ('data',('weather.csv',open('weather.csv','rb'),'text/csv'))
    ]
    
    
    response = requests.put(url=test_endpoint, headers=headers, files=files, data=payload)
    assert response.status_code == 200, "Update Dataset failed"
    logger.info(response.json())

def test_get_dataset(access_token,endpoint,request):
    dataset_id= request.config.cache.get('dataset_id', None)
    uri = "/v2/language/datasets/{}".format(dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    payload={}    
    response = requests.get(url=test_endpoint, headers=headers, data=payload)
    assert response.status_code == 200,  "Get Dataset failed"
    logger.info(response.json())

@pytest.mark.dependency()
def test_get_examples(access_token, endpoint, request):
    dataset_id= request.config.cache.get('dataset_id', None)
    uri = "/v2/language/datasets/{}/examples".format(dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
      
    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Get Examples call failed"
    logger.info(response.json())

@pytest.mark.dependency()
def test_get_labels(access_token, endpoint, request):
    dataset_id= request.config.cache.get('dataset_id', None)
    uri = "/v2/language/examples/{}/label/1".format(dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
      
    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Get Label call failed"
    logger.info(response.json())

@pytest.mark.dependency(depends=["test_get_examples", "test_get_labels"])
def test_delete_dataset(access_token, endpoint, request):
    dataset_id= request.config.cache.get('dataset_id', None)
    uri = "/v2/language/datasets/{}".format(dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    response = requests.delete(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Delete Dataset failed"
    logger.info(response.json())

@pytest.mark.skip("Train model call skipped. Please test it manually")
def test_train_model(access_token, endpoint, model_dataset_id, request):
    uri = "/v2/language/train"
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    payload ={}

    files = {
        'name':'Weather Intent Model',
        'datasetId': model_dataset_id,
        'trainParams': '{"trainSplitRatio":"0.7"}'
    }
      
    response = requests.post(url=test_endpoint, headers=headers, data=payload, files=files)
    assert response.status_code == 200, "Train a model call failed"
    model_id =  response.json()["modelId"]
    request.config.cache.set('model_id', model_id)
    logger.info(response.json())

@pytest.mark.skipif(os.environ.get("TRAINED_MODEL_ID") == None, reason="to test get training status, a trained model id is needed")
def test_get_train_status(access_token, endpoint, request,trained_model_id):
    model_id= request.config.cache.get('model_id', None)
    if trained_model_id != None:
        model_id = trained_model_id
    uri = "/v2/language/train/{}".format(model_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Train status call failed"
    logger.info(response.json())

def get_train_status(access_token, endpoint, trained_model_id):
    if trained_model_id != None:
        model_id = trained_model_id
    uri = "/v2/language/train/{}".format(model_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Get Train status call failed"
    logger.info(response.json())
    return response.json()['status']

@pytest.mark.parametrize("lc",["","/lc?offset=0&count=3"])
@pytest.mark.skipif(os.environ.get("TRAINED_MODEL_ID") == None, reason="to test get training status, a trained model id is needed")
def test_get_model_metrics(access_token, endpoint, request,lc, trained_model_id):
    model_id= request.config.cache.get('model_id', None)
    if trained_model_id != None:
        model_id = trained_model_id
    model_status = get_train_status(access_token, endpoint, model_id)
    if model_status != "SUCCEEDED" and trained_model_id is None:
        pytest.skip("Model metrics/LC call skipped. Model is not ready")
    else:
        model_id= trained_model_id
    uri = "/v2/language/models/{}{}".format(model_id,lc)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Model Metrics/LC call failed"
    logger.info(response.json())

def test_get_all_models(access_token, endpoint, model_dataset_id):
    uri = "/v2/language/datasets/{}/models".format(model_dataset_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    response = requests.get(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Get All models call failed"
    logger.info(response.json())

@pytest.mark.parametrize("prediction_type,is_GLOBAL_MODEL",[("intent",True),("entities",True),("sentiment",True),("intent",False)])
def test_prediction(access_token,endpoint,prediction_type,request,is_GLOBAL_MODEL,trained_model_id):
    model_id = request.config.cache.get('model_id', None)
    model_status = None
    if os.environ.get("TRAINED_MODEL_ID") != None:
        model_id = trained_model_id
        model_status = get_train_status(access_token, endpoint, model_id)
    logger.info(model_id)
    uri = "/v2/language/{}".format(prediction_type)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    payload = {}

    if prediction_type == "intent":
        if is_GLOBAL_MODEL:
            model_id = "GlobalIntentModel"
        elif trained_model_id is None:
            pytest.skip("Prediction call skipped. No trained model id is provided")
        elif model_status != "SUCCEEDED":
            pytest.skip("Prediction call skipped. Model is not ready")
        else:
            model_id = trained_model_id
        files = {
            'document': 'what is the weather in los angeles',
            'modelId': model_id,
        }
    if prediction_type == "entities":
        files = {
            'document': 'Marc Benioff, the CEO of Salesforce, gave the keynote speech at the conference in Paris last week',
        }
    if prediction_type == "sentiment":
        files = {
            'document': 'The presentation was great and I learned a lot',
            'modelId': 'CommunitySentiment'
        }

    response = requests.post(url=test_endpoint, headers=headers, data=payload, files=files)
    assert response.status_code == 200, "Test Predictions call failed for type {} \n".format(prediction_type)
    logger.info(response.text)

@pytest.mark.parametrize("model_id",["OCRModel","tabulatev2"])
def test_ocr(access_token,endpoint,model_id):
    uri = "/v2/vision/ocr"
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    payload = {'modelId' : model_id}

    files=[
        ('sampleContent',('emergency-evacuation-route-signpost.jpg',open('emergency-evacuation-route-signpost.jpg','rb'),'image/jpeg'))
    ]   

    response = requests.post(url=test_endpoint, headers=headers, data=payload, files=files)
    assert response.status_code == 200, "OCR prediction call failed"
    logger.info(response.json())

@pytest.mark.skip("Retrain model call skipped. Please test it manually")
def test_retrain_model(access_token, endpoint, request, trained_model_id):
    model_id= request.config.cache.get('model_id', None)
    assert model_id != None, "Retrain a model call failed. Model ID is Invalid"
    uri = "/v2/language/retrain"
    test_endpoint = endpoint+uri

    model_status = get_train_status(access_token, endpoint, model_id)
    if model_status != "SUCCEEDED" and trained_model_id is None :
        pytest.skip("Retrain model call skipped. Model is not ready.")
    else: 
        model_id = trained_model_id
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }
    payload ={}

    files = {
        'modelId': model_id,
    }
      
    response = requests.post(url=test_endpoint, headers=headers, data=payload, files=files)
    assert response.status_code == 200, "Retrain a model call failed"
    logger.info(response.json())
    
@pytest.mark.skip("Delete model call skipped. Please test it manually")
def test_delete_model(access_token, endpoint, request,trained_model_id):
    model_id = request.config.cache.get('model_id', None)
    assert model_id != None, "Delete model call failed. Model ID is Invalid"

    model_status = get_train_status(access_token, endpoint, model_id)
    if model_status != "SUCCEEDED" and trained_model_id is None:
        pytest.skip("Delete model call skipped. Model is not ready.")
    else: 
        model_id = trained_model_id

    uri = "/v2/language/models/{}".format(model_id)
    test_endpoint = endpoint+uri
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Cache-Control': 'no-cache',
    }

    response = requests.delete(url=test_endpoint, headers=headers)
    assert response.status_code == 200, "Model Delete call failed"
    logger.info(response.json())