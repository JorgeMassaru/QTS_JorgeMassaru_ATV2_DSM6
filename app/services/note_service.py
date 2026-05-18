"""
Arquivo responsável pelas regras de negócio das notas.

Aqui não trabalhamos diretamente com HTTP.
Este arquivo apenas cuida da lógica:
- criar nota
- listar notas
- buscar por ID
- atualizar
- excluir
- fixar / desfixar nota
- filtrar por categoria
"""

VALID_CATEGORIES = ["pessoal", "trabalho", "estudo", "ideia", "outro"]

# Lista que simula o banco de dados
notes = []

# Variável para controlar o ID automático das notas
current_id = 1


def reset_notes():
    """
    Reinicia o banco em memória.

    Essa função será muito útil nos testes, pois garante que cada teste
    comece com a lista de notas vazia.
    """
    global current_id

    notes.clear()
    current_id = 1


def get_all_notes():
    """
    Retorna todas as notas cadastradas.
    """
    return notes


def get_note_by_id(note_id):
    """
    Busca uma nota pelo ID.

    Se encontrar, retorna a nota.
    Se não encontrar, retorna None.
    """
    return next((note for note in notes if note["id"] == note_id), None)


def create_note(data):
    """
    Cria uma nova nota.

    Antes de criar, verifica se já existe uma nota com o mesmo título.
    Se existir, retorna None para impedir duplicidade.

    Campos suportados: title (obrigatório), content, category.
    Categoria inválida é substituída por 'outro'.
    """
    global current_id

    for note in notes:
        if note["title"].lower() == data["title"].lower():
            return None

    category = data.get("category", "outro")
    if category not in VALID_CATEGORIES:
        category = "outro"

    note = {
        "id": current_id,
        "title": data["title"],
        "content": data.get("content", ""),
        "category": category,
        "pinned": False,
    }

    notes.append(note)
    current_id += 1

    return note


def update_note(note_id, data):
    """
    Atualiza título e/ou conteúdo de uma nota existente.

    Se a nota não existir, retorna None.
    """
    note = get_note_by_id(note_id)

    if not note:
        return None

    if "title" in data:
        note["title"] = data["title"]

    if "content" in data:
        note["content"] = data["content"]

    if "category" in data:
        category = data["category"]
        note["category"] = category if category in VALID_CATEGORIES else "outro"

    return note


def delete_note(note_id):
    """
    Remove uma nota pelo ID.

    Se a nota existir, remove e retorna True.
    Se não existir, retorna False.
    """
    note = get_note_by_id(note_id)

    if not note:
        return False

    notes.remove(note)

    return True


def pin_note(note_id):
    """
    Marca uma nota como fixada (pinned = True).

    Se a nota não existir, retorna None.
    """
    note = get_note_by_id(note_id)

    if not note:
        return None

    note["pinned"] = True

    return note


def unpin_note(note_id):
    """
    Remove o destaque de uma nota (pinned = False).

    Se a nota não existir, retorna None.
    """
    note = get_note_by_id(note_id)

    if not note:
        return None

    note["pinned"] = False

    return note


def get_pinned_notes():
    """
    Retorna apenas as notas fixadas.
    """
    return [note for note in notes if note["pinned"]]


def get_notes_by_category(category):
    """
    Retorna apenas as notas que pertencem à categoria informada.
    """
    return [note for note in notes if note["category"] == category]
