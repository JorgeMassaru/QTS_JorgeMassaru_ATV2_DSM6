"""
Arquivo responsável pelas rotas da API de notas.

Aqui lidamos com:
- requisições HTTP
- respostas JSON
- códigos de status HTTP

A regra de negócio fica no arquivo note_service.py.
"""

from flask import Blueprint, jsonify, request

from app.services.note_service import (
    create_note,
    delete_note,
    get_all_notes,
    get_note_by_id,
    get_notes_by_category,
    get_pinned_notes,
    pin_note,
    unpin_note,
    update_note,
)

# Cria um Blueprint para organizar as rotas de notas
note_bp = Blueprint("notes", __name__, url_prefix="/notes")


@note_bp.route("/status", methods=["GET"])
def status():
    """
    Rota simples para verificar se a API está funcionando.
    """
    return jsonify({"status": "ok"}), 200


@note_bp.route("", methods=["GET"])
def list_notes():
    """
    Lista todas as notas cadastradas.
    """
    return jsonify(get_all_notes()), 200


@note_bp.route("/pinned", methods=["GET"])
def list_pinned():
    """
    Lista apenas as notas fixadas.
    """
    return jsonify(get_pinned_notes()), 200


@note_bp.route("/category/<string:category>", methods=["GET"])
def list_by_category(category):
    """
    Lista notas filtradas por categoria.
    """
    return jsonify(get_notes_by_category(category)), 200


@note_bp.route("/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """
    Busca uma nota específica pelo ID.
    """
    note = get_note_by_id(note_id)

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note), 200


@note_bp.route("", methods=["POST"])
def create():
    """
    Cria uma nova nota.

    Espera receber um JSON no formato:
    {
        "title": "Nome da nota",
        "content": "Conteúdo opcional",
        "category": "estudo"
    }
    """
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    note = create_note(data)

    if note is None:
        return jsonify({"error": "Note with this title already exists"}), 409

    return jsonify(note), 201


@note_bp.route("/<int:note_id>", methods=["PUT"])
def update(note_id):
    """
    Atualiza título e/ou conteúdo de uma nota existente.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    note = update_note(note_id, data)

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note), 200


@note_bp.route("/<int:note_id>", methods=["DELETE"])
def delete(note_id):
    """
    Remove uma nota existente.
    """
    deleted = delete_note(note_id)

    if not deleted:
        return jsonify({"error": "Note not found"}), 404

    return "", 204


@note_bp.route("/<int:note_id>/pin", methods=["PATCH"])
def pin(note_id):
    """
    Fixa uma nota (pinned = True).
    """
    note = pin_note(note_id)

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note), 200


@note_bp.route("/<int:note_id>/unpin", methods=["PATCH"])
def unpin(note_id):
    """
    Remove o destaque de uma nota (pinned = False).
    """
    note = unpin_note(note_id)

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify(note), 200
