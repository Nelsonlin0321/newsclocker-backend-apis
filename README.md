# newsclocker-backend-apis

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
                  --port 8080
# or
sh boot.sh
```