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
                  --reload-dir ./app
                  --host localhost
                  --port 8000
# or
sh boot.sh
```


## Build and Run Docker
```shell
image_name=newsclocker-backend-apis
docker build -t ${image_name}:latest -f ./Dockerfile .
docker run --env-file .env.docker -p 8080:8080 -it --rm --name ${image_name} ${image_name}:latest
```

##
```shell
curl -H "X-API-Key: 123" http://localhost:8000/api/health_check
```