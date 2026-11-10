import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

# Aislar la base de datos incluso durante el import de la aplicación.
_tmp = tempfile.TemporaryDirectory()
os.environ["DB_PATH"] = str(Path(_tmp.name) / "gastos.db")
from main import app

def test_flujo_y_metricas():
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert "Comida" in client.get("/api/categorias").json()
        body = {"descripcion": "Almuerzo / ñ", "monto": 250.5, "categoria": "Comida"}
        response = client.post("/api/gastos", json=body)
        assert response.status_code == 200
        assert response.json()["id"] > 0
        assert client.get("/api/gastos").json()[0]["descripcion"] == body["descripcion"]
        metrics = client.get("/metrics").text
        assert 'gastos_creados_total{categoria="Comida"}' in metrics
        assert "http_requests_total" in metrics
        assert client.get("/").status_code == 404
        cors = client.options("/api/gastos", headers={"Origin":"http://localhost:8080", "Access-Control-Request-Method":"POST", "Access-Control-Request-Headers":"content-type"})
        assert cors.headers["access-control-allow-origin"] == "http://localhost:8080"
        assert client.post("/api/gastos", json={"monto":"incorrecto"}).status_code == 422
