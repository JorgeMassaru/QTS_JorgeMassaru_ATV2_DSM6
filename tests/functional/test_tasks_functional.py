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


def test_full_note_lifecycle(client):
    """Fluxo completo: criar → buscar → atualizar → excluir."""
    created = client.post(
        "/notes", json={"title": "Ciclo completo", "category": "estudo"}
    )
    note_id = created.get_json()["id"]

    fetched = client.get(f"/notes/{note_id}")
    assert fetched.status_code == 200
    assert fetched.get_json()["title"] == "Ciclo completo"

    updated = client.put(
        f"/notes/{note_id}",
        json={"title": "Ciclo atualizado", "content": "Novo conteúdo"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["title"] == "Ciclo atualizado"

    deleted = client.delete(f"/notes/{note_id}")
    assert deleted.status_code == 204

    final = client.get(f"/notes/{note_id}")
    assert final.status_code == 404


def test_multiple_notes_listing(client):
    """Criar várias notas e verificar listagem completa."""
    client.post("/notes", json={"title": "Nota 1"})
    client.post("/notes", json={"title": "Nota 2"})
    client.post("/notes", json={"title": "Nota 3"})

    response = client.get("/notes")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 3


def test_invalid_note_creation(client):
    """Criar nota sem título deve retornar erro."""
    response = client.post("/notes", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "title is required"


# ── 3 novos testes funcionais ─────────────────────────────────────────────────


def test_pin_and_list_pinned_notes_flow(client):
    """
    Fluxo: criar notas → fixar uma → listar fixadas.
    Verifica que apenas a nota fixada aparece em /notes/pinned.
    """
    n1 = client.post("/notes", json={"title": "Fixar esta"}).get_json()
    client.post("/notes", json={"title": "Não fixar esta"})

    client.patch(f"/notes/{n1['id']}/pin")

    response = client.get("/notes/pinned")
    pinned = response.get_json()

    assert response.status_code == 200
    assert len(pinned) == 1
    assert pinned[0]["title"] == "Fixar esta"
    assert pinned[0]["pinned"] is True


def test_category_filter_flow(client):
    """
    Fluxo: criar notas com categorias diferentes → filtrar por categoria.
    Garante que o filtro retorna somente as notas corretas.
    """
    client.post("/notes", json={"title": "Estudar Python", "category": "estudo"})
    client.post("/notes", json={"title": "Fazer compras", "category": "pessoal"})
    client.post("/notes", json={"title": "Estudar SQL", "category": "estudo"})

    response = client.get("/notes/category/estudo")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    titles = [n["title"] for n in data]
    assert "Estudar Python" in titles
    assert "Estudar SQL" in titles


def test_pin_unpin_flow(client):
    """
    Fluxo: criar nota → fixar → verificar fixada → desfixar → verificar.
    """
    note = client.post("/notes", json={"title": "Vai e vem"}).get_json()
    note_id = note["id"]

    pinned = client.patch(f"/notes/{note_id}/pin").get_json()
    assert pinned["pinned"] is True

    pinned_list = client.get("/notes/pinned").get_json()
    assert any(n["id"] == note_id for n in pinned_list)

    unpinned = client.patch(f"/notes/{note_id}/unpin").get_json()
    assert unpinned["pinned"] is False

    pinned_list_after = client.get("/notes/pinned").get_json()
    assert not any(n["id"] == note_id for n in pinned_list_after)