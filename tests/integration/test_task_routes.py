import pytest

from app import create_app
from app.services.note_service import reset_notes


@pytest.fixture
def client():
    reset_notes()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Testes base ────────────────────────────────────────────────────────────────


def test_status_route(client):
    response = client.get("/notes/status")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_note_route(client):
    response = client.post("/notes", json={"title": "Nota de integração"})

    assert response.status_code == 201
    assert response.get_json()["title"] == "Nota de integração"


def test_list_notes_route(client):
    client.post("/notes", json={"title": "Nota A"})
    client.post("/notes", json={"title": "Nota B"})

    response = client.get("/notes")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_note_by_id_route(client):
    created = client.post("/notes", json={"title": "Buscar por ID"})
    note_id = created.get_json()["id"]

    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.get_json()["title"] == "Buscar por ID"


def test_delete_note_route(client):
    created = client.post("/notes", json={"title": "Excluir integração"})
    note_id = created.get_json()["id"]

    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 204


# ── 5 novos testes de integração ──────────────────────────────────────────────


def test_create_note_missing_title_returns_400(client):
    """Criar nota sem título deve retornar 400."""
    response = client.post("/notes", json={"content": "Só conteúdo"})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_duplicate_note_returns_409(client):
    """Criar nota com título duplicado deve retornar 409 Conflict."""
    client.post("/notes", json={"title": "Duplicata"})

    response = client.post("/notes", json={"title": "Duplicata"})

    assert response.status_code == 409


def test_get_nonexistent_note_returns_404(client):
    """Buscar nota com ID inexistente deve retornar 404."""
    response = client.get("/notes/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Note not found"


def test_pin_note_route(client):
    """Fixar nota via rota PATCH deve retornar nota com pinned=True."""
    created = client.post("/notes", json={"title": "Fixar"})
    note_id = created.get_json()["id"]

    response = client.patch(f"/notes/{note_id}/pin")

    assert response.status_code == 200
    assert response.get_json()["pinned"] is True


def test_filter_by_category_route(client):
    """Filtro por categoria deve retornar apenas notas da categoria."""
    client.post("/notes", json={"title": "Nota estudo", "category": "estudo"})
    client.post("/notes", json={"title": "Nota pessoal", "category": "pessoal"})

    response = client.get("/notes/category/estudo")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["category"] == "estudo"