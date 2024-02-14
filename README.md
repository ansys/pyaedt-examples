# rep-python-repo-template
Template for REP python repos

### Prerequisites

Install pre-commit in your `global` python using

```
python -m pip install pre-commit
```
### Build process

#### On linux:

```
python3 -m venv dev_env
source dev_env/bin/activate
python build.py dev
```
#### On windows:
```    
python3 -m venv dev_env
dev_env/Scripts/activate
python build.py dev
```
### Building docker image (does a freeze)

```
docker build -f docker\Dockerfile.default --secret id=netrc,src=c:/Users/USER/.netrc -t rep-mock-solver:latest .

also useful for debugging

docker build --no-cache -f docker\Dockerfile.default --progress=plain --secret id=netrc,src=c:/Users/USER/.netrc -t rep-mock-solver:latest .

or use docker-compose

docker-compose -f docker-compose.yaml
```

### github build:

ci_cd.yml github workflow will post the frozen executable and wheel as artifacts