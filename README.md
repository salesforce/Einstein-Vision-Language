## Description

A python implementation for Einstein Vision and Language. Use the power of natural language processing to connect with your customers in entirely new ways by discovering insights from unstructured text data.
This repo is created for automated testing for all endpoint/train new model / measure metrics and various other features using just one command.
For details about API - please check: https://developer.salesforce.com/docs/analytics/einstein-vision-language/overview

## Pre-requisite

Please make sure you have [Docker](https://www.docker.com/) installed. 
Also, you need to generate REFRESH_TOKEN as a one time setup. 
Please use `generate_refresh_token.py` file and update "pem_file" and "my_email" values as indicated in the file.
After that please run `python generate_refresh_token.py`. This will create a REFRESH_TOKEN. Please save it for future usage.
Please note- REFRESH_TOKEN is sensitive data. Please use appropriate caution to secure it.

## How to run

Please export below environment variables and then execute ./run.sh
```
export REFRESH_TOKEN=<REFRESH_TOKEN>
./run.sh
```

## Command line options
REFRESH_TOKEN  - provide the refresh token

TRAINED_MODEL_ID - use an existing trained model id. This is useful for testing training metrics and training status.
Also, by default the predictions calls are tested (intent, sentiment, entity) only for GlobalModel(trained with public data).
If you supply a TRAINED_MODEL_ID, then prediction call is tested for your model too.


## Training new model

By default training a new model test is skipped using  `@pytest.mark.skip` annotation as training a model takes time and its a time-consuming operation. The recommended approach is to train one model and then use that for subsequent validations. To train a model,
please comment out above line in the `test_train_model` function definition. 


## Exit code

Exit code 0
All tests were collected and passed successfully

Exit code 1
Tests were collected and run but some of the tests failed

Exit code 2
Test execution was interrupted by the user

Exit code 3
Internal error happened while executing tests

Exit code 4
pytest command line usage error

Exit code 5
No tests were collected

More details are [here](https://docs.pytest.org/en/7.1.x/reference/exit-codes.html).



