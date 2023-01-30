# falert

## Setup

### Install dependencies (apt)

```
sudo apt-get update
sudo apt-get -y install curl
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo bash -
sudo apt-get install -y libsqlite3-dev nodejs python3 python3-venv python3-pip gcc g++ make libgeos-dev
```

### Install dependencies (npm)

```
npm install
```

### Create virtualenv

```
python3 -m venv .python3-environment
```

### Install dependencies (pip)

```
. .python3-environment/bin/activate
python3 -m pip install -r requirements.txt
```

## Build static files

```
npm run build
```

## Run the applications

```
. .python3-environment/bin/activate
python3 -m 'falert.backend.http'
python3 -m 'falert.backend.matcher'
python3 -m 'falert.backend.harvester'
python3 -m 'falert.backend.notifier
```

## Perform application checks

```
npm run lint
. .python3-environment/bin/activate
python3 -m black --check falert/backend
python3 -m pylint falert/backend
python3 -m mypy falert/backend
```
