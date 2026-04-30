# Mission 15 Docker Workflow

## Structure

- `researcher1`: trains the regression model and writes artifacts to `/shared`
- `researcher2`: runs JupyterLab and inference with the trained model
- `shared`: shared artifact directory for `model.pkl`, `test.csv`, `metrics.json`, and `result.csv`
- `tests`: workflow tests for training and inference scripts

## Local Test

```powershell
python -m pip install -r requirements.txt
python -m pytest tests
python researcher1/train_model.py --train-path researcher1/data/train.csv --test-path researcher1/data/test.csv --output-dir shared
python researcher2/inference.py --model-path shared/model.pkl --test-path shared/test.csv --result-path shared/result.csv
```

## Docker Run

```powershell
docker compose pull researcher1
docker compose build researcher2
docker compose run --rm researcher1
docker compose run --rm researcher2 python inference.py --model-path /shared/model.pkl --test-path /shared/test.csv --result-path /shared/result.csv
```

To open the JupyterLab container:

```powershell
docker compose up researcher2
```

Then open `http://localhost:8888`.

## Docker Hub

Researcher 1 Docker Hub image:

https://hub.docker.com/r/ming2tofu33/mission15-researcher1
