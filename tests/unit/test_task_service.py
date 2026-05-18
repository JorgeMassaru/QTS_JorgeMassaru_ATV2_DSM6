import pytest

from app.services.note_service import (
    VALID_CATEGORIES,
    create_note,
    delete_note,
    get_all_notes,
    get_note_by_id,
    get_notes_by_category,
    get_pinned_notes,
    pin_note,
    reset_notes,
    unpin_note,
    update_note,
)


@pytest.fixture(autouse=True)
def clear_notes():
    """Garante lista limpa antes de cada teste."""
    reset_notes()


# ── Testes base ────────────────────────────────────────────────────────────────


def test_create_note_basic():
    note = create_note({"title": "Minha primeira nota"})

    assert note["id"] == 1
    assert note["title"] == "Minha primeira nota"
    assert note["completed"] is False if "completed" in note else True
    assert note["pinned"] is False


def test_create_note_returns_correct_fields():
    note = create_note({"title": "Campos", "content": "Texto", "category": "estudo"})

    assert "id" in note
    assert "title" in note
    assert "content" in note
    assert "category" in note
    assert "pinned" in note


def test_get_all_notes_empty():
    assert get_all_notes() == []


def test_get_all_notes_with_items():
    create_note({"title": "Nota 1"})
    create_note({"title": "Nota 2"})

    assert len(get_all_notes()) == 2


def test_get_note_by_id_found():
    note = create_note({"title": "Buscar por ID"})

    result = get_note_by_id(note["id"])

    assert result["title"] == "Buscar por ID"


def test_get_note_by_id_not_found():
    result = get_note_by_id(999)

    assert result is None


def test_update_note_title():
    note = create_note({"title": "Título original"})

    updated = update_note(note["id"], {"title": "Título atualizado"})

    assert updated["title"] == "Título atualizado"


def test_update_note_not_found():
    result = update_note(999, {"title": "Não existe"})

    assert result is None


def test_delete_note():
    note = create_note({"title": "Apagar isso"})

    result = delete_note(note["id"])

    assert result is True
    assert get_all_notes() == []


def test_delete_note_not_found():
    result = delete_note(999)

    assert result is False


def test_create_duplicate_note_returns_none():
    create_note({"title": "Duplicada"})

    result = create_note({"title": "Duplicada"})

    assert result is None


# ── 10 novos testes unitários ──────────────────────────────────────────────────


def test_create_note_case_insensitive_duplicate():
    """Duplicata deve ser detectada independente de maiúsculas/minúsculas."""
    create_note({"title": "Reunião"})

    result = create_note({"title": "REUNIÃO"})

    assert result is None


def test_create_note_default_category_is_outro():
    """Categoria padrão deve ser 'outro' quando não informada."""
    note = create_note({"title": "Sem categoria"})

    assert note["category"] == "outro"


def test_create_note_invalid_category_falls_back_to_outro():
    """Categoria inválida deve ser substituída por 'outro'."""
    note = create_note({"title": "Categoria inválida", "category": "inexistente"})

    assert note["category"] == "outro"


def test_create_note_with_valid_category():
    """Categoria válida deve ser persistida corretamente."""
    note = create_note({"title": "Nota de estudo", "category": "estudo"})

    assert note["category"] == "estudo"


def test_create_note_stores_content():
    """Conteúdo da nota deve ser armazenado."""
    note = create_note({"title": "Com conteúdo", "content": "Texto detalhado"})

    assert note["content"] == "Texto detalhado"


def test_ids_are_sequential():
    """IDs devem ser incrementados sequencialmente."""
    n1 = create_note({"title": "Primeira"})
    n2 = create_note({"title": "Segunda"})
    n3 = create_note({"title": "Terceira"})

    assert n1["id"] == 1
    assert n2["id"] == 2
    assert n3["id"] == 3


def test_reset_notes_clears_all():
    """reset_notes deve limpar todas as notas e reiniciar o ID."""
    create_note({"title": "Antes do reset"})
    reset_notes()

    assert get_all_notes() == []

    note = create_note({"title": "Após reset"})
    assert note["id"] == 1


def test_get_notes_by_category_returns_correct_notes():
    """Filtro por categoria deve retornar apenas as notas corretas."""
    create_note({"title": "Estudar Flask", "category": "estudo"})
    create_note({"title": "Comprar pão", "category": "pessoal"})
    create_note({"title": "Estudar Pytest", "category": "estudo"})

    result = get_notes_by_category("estudo")

    assert len(result) == 2
    assert all(n["category"] == "estudo" for n in result)


def test_get_notes_by_category_empty_when_none_match():
    """Deve retornar lista vazia quando nenhuma nota pertence à categoria."""
    create_note({"title": "Nota pessoal", "category": "pessoal"})

    result = get_notes_by_category("trabalho")

    assert result == []


def test_update_note_content_only():
    """Deve atualizar apenas o conteúdo sem alterar o título."""
    note = create_note({"title": "Título fixo", "content": "Conteúdo antigo"})

    updated = update_note(note["id"], {"content": "Conteúdo novo"})

    assert updated["title"] == "Título fixo"
    assert updated["content"] == "Conteúdo novo"


# ── Testes TDD: pin/unpin ──────────────────────────────────────────────────────


def test_pin_note():
    """(TDD - GREEN) Fixar uma nota deve marcar pinned como True."""
    note = create_note({"title": "Fixar esta nota"})

    pinned = pin_note(note["id"])

    assert pinned["pinned"] is True


def test_pin_note_not_found():
    """(TDD - GREEN) Fixar nota inexistente deve retornar None."""
    result = pin_note(999)

    assert result is None


def test_unpin_note():
    """(TDD - GREEN) Desafixar uma nota deve marcar pinned como False."""
    note = create_note({"title": "Desfixar esta nota"})
    pin_note(note["id"])

    unpinned = unpin_note(note["id"])

    assert unpinned["pinned"] is False


def test_get_pinned_notes_returns_only_pinned():
    """(TDD - GREEN) Deve retornar apenas as notas fixadas."""
    n1 = create_note({"title": "Fixada"})
    create_note({"title": "Não fixada"})
    pin_note(n1["id"])

    pinned = get_pinned_notes()

    assert len(pinned) == 1
    assert pinned[0]["title"] == "Fixada"


def test_valid_categories_list():
    """Confirma que a lista de categorias contém os valores esperados."""
    expected = {"pessoal", "trabalho", "estudo", "ideia", "outro"}

    assert set(VALID_CATEGORIES) == expected