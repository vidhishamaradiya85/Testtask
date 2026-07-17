import pytest

def test_create_note_success(client, valid_headers):
    # 1. Create a note successfully -> 201, correct response shape
    payload = {
        "title": "Test Note",
        "body": "This is a test note.",
        "tags": ["test", "api"]
    }
    response = client.post("/notes", json=payload, headers=valid_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]
    assert data["tags"] == payload["tags"]
    assert "created_at" in data
    assert "updated_at" in data

def test_create_note_missing_title(client, valid_headers):
    # 2. Create a note with missing title -> 422
    payload = {
        "body": "This note has no title.",
        "tags": ["test"]
    }
    response = client.post("/notes", json=payload, headers=valid_headers)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data

def test_get_nonexistent_note(client, valid_headers):
    # 3. Get a note that doesn't exist -> 404
    response = client.get("/notes/9999", headers=valid_headers)
    assert response.status_code == 404

def test_update_note_success(client, valid_headers):
    # 4. Update a note successfully -> updated_at changes, fields reflect changes
    # First create a note
    payload = {
        "title": "Original Title",
        "body": "Original Body",
        "tags": ["original"]
    }
    create_resp = client.post("/notes", json=payload, headers=valid_headers)
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]
    original_updated_at = create_resp.json()["updated_at"]

    # Now update the note
    update_payload = {
        "title": "Updated Title",
        "tags": ["updated"]
    }
    update_resp = client.put(f"/notes/{note_id}", json=update_payload, headers=valid_headers)
    assert update_resp.status_code == 200
    
    data = update_resp.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Original Body" # Unchanged
    assert data["tags"] == ["updated"]
    assert data["updated_at"] != original_updated_at

def test_delete_note(client, valid_headers):
    # 5. Delete a note -> 204, then GET on it -> 404
    payload = {
        "title": "To be deleted",
        "body": "Delete me"
    }
    create_resp = client.post("/notes", json=payload, headers=valid_headers)
    note_id = create_resp.json()["id"]

    # Delete
    delete_resp = client.delete(f"/notes/{note_id}", headers=valid_headers)
    assert delete_resp.status_code == 204

    # GET should return 404
    get_resp = client.get(f"/notes/{note_id}", headers=valid_headers)
    assert get_resp.status_code == 404

def test_search_by_tag(client, valid_headers):
    # 6. Search by tag returns only matching notes
    client.post("/notes", json={"title": "Note 1", "body": "...", "tags": ["python", "fastapi"]}, headers=valid_headers)
    client.post("/notes", json={"title": "Note 2", "body": "...", "tags": ["javascript"]}, headers=valid_headers)
    client.post("/notes", json={"title": "Note 3", "body": "...", "tags": ["python"]}, headers=valid_headers)

    response = client.get("/notes/search?tag=python", headers=valid_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for note in data:
        assert "python" in note["tags"]

def test_search_by_keyword(client, valid_headers):
    # 7. Search by keyword matches title and body, case-insensitive
    client.post("/notes", json={"title": "FastAPI is great", "body": "It is a web framework"}, headers=valid_headers)
    client.post("/notes", json={"title": "Django", "body": "Another python framework, also great for web"}, headers=valid_headers)
    client.post("/notes", json={"title": "Flask", "body": "A microframework"}, headers=valid_headers)

    # Search for "Great"
    response = client.get("/notes/search?q=Great", headers=valid_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [n["title"] for n in data]
    assert "FastAPI is great" in titles
    assert "Django" in titles

def test_request_without_api_key(client):
    # 8. Request without API key header -> 401
    response = client.get("/notes")
    assert response.status_code == 401
    assert "error" in response.json()

def test_request_with_wrong_api_key(client):
    # 9. Request with wrong API key -> 401
    headers = {"X-API-Key": "wrong-key"}
    response = client.get("/notes", headers=headers)
    assert response.status_code == 401
    assert "error" in response.json()
