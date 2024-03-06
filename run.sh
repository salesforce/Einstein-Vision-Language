docker build --rm -t eai_smoke_test:latest .   
docker run --rm --user $(id -u):$(id -g) -e REFRESH_TOKEN=${REFRESH_TOKEN} -v `pwd`:/tmp eai_smoke_test:latest --target-env ${TARGET_ENV:-prod} --retries 3 --retry-delay 15 --use-trained-model-id ${TRAINED_MODEL_ID:-None} --no-header -v
EXIT_CODE=$(echo $?)
echo "EXIT_CODE=$EXIT_CODE"

if [ $EXIT_CODE -ne 0 ]; then
    exit 1
fi
exit $EXIT_CODE
