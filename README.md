# newsclocker-backend-apis

## Run Locally
```shell
# create a python environment
python -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# run API locally
source .venv/bin/activate
source .env
uvicorn main:app --reload \
                  --reload-dir ./app \
                  --host localhost \
                  --port 8080
# or
sh boot.sh
```


## Build and Run Docker
```shell
image_name=newsclocker-backend-apis
docker build -t ${image_name}:latest -f ./Dockerfile . --platform linux/amd64
docker run --env-file .env.docker -p 8080:8080 -it --rm --name ${image_name} ${image_name}:latest
```

##
```shell
curl -H "X-API-Key: 123" http://localhost:8080/api/health_check
```

## Build and Run Lambda Docker
```shell
image_name=newsclocker-backend-apis-lambda
docker build -t ${image_name}:latest -f ./Dockerfile.aws.lambda .
```
```shell
image_name=newsclocker-backend-apis-lambda
docker build -t ${image_name}:latest -f ./Dockerfile.aws.lambda . --platform linux/arm64/v8
```

```shell
docker run --env-file .env.docker -p 9000:8080 --name ${image_name} -it --rm ${image_name}:latest
```

```shell
image_name=newsclocker-backend-apis-lambda
docker exec -it ${image_name} /bin/bash
```

```shell
# TEST healthcheck
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/api/health_check",
    "path": "/api/health_check",
    "httpMethod": "GET",
    "requestContext": {
    },
    "isBase64Encoded": false
}'
```