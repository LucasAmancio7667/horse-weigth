def test_health_reports_database_ok_and_storage_down(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok", "storage": "unavailable"}


def test_create_and_list_animals(client):
    r = client.post(
        "/api/animals",
        json={"name": "Trovão", "breed": "Mangalarga Marchador", "sex": "male", "withers_height_cm": 150},
    )
    assert r.status_code == 201
    created = r.json()
    assert created["id"] == 1 and created["name"] == "Trovão" and created["is_pregnant"] is False

    r = client.get("/api/animals")
    assert [a["name"] for a in r.json()] == ["Trovão"]

    assert client.get(f"/api/animals/{created['id']}").json()["breed"] == "Mangalarga Marchador"


def test_get_missing_animal_returns_404(client):
    assert client.get("/api/animals/999").status_code == 404


def test_create_animal_validates_input(client):
    assert client.post("/api/animals", json={"name": ""}).status_code == 422
    assert client.post("/api/animals", json={"name": "X", "withers_height_cm": -5}).status_code == 422
    assert client.post("/api/animals", json={"name": "X", "sex": "dragon"}).status_code == 422
