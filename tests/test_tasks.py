# FILE: tests/test_tasks.py

def test_create_task_valid_returns_201_with_full_body(client):
    r = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Build API",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Rashed",
        },
    )

    assert r.status_code == 201

    data = r.json()
    assert "id" in data
    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Build API"
    assert data["status"] == "ToDo"
    assert data["priority"] == "High"
    assert data["assignee"] == "Rashed"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={})

    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})

    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post(
        "/tasks",
        json={
            "title": "Task",
            "priority": "Urgent",
        },
    )

    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post(
        "/tasks",
        json={
            "title": "Task",
            "unknown": "value",
        },
    )

    assert r.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    r = client.get("/tasks", params={"status": "Done"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post(
        "/tasks",
        json={
            "title": "High Priority",
            "priority": "High",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Low Priority",
            "priority": "Low",
        },
    )

    r = client.get("/tasks", params={"priority": "High"})

    assert r.status_code == 200

    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "High Priority"
    assert data[0]["priority"] == "High"


def test_list_tasks_filter_by_text_status_priority_and_assignee_returns_matches(client):
    client.post(
        "/tasks",
        json={
            "title": "Plan launch",
            "description": "Prepare rollout",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Rashed",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Draft summary",
            "description": "Review notes",
            "status": "InProgress",
            "priority": "High",
            "assignee": "Mina",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Ship release",
            "description": "Publish package",
            "status": "Done",
            "priority": "Low",
            "assignee": "Rashed",
        },
    )

    r = client.get(
        "/tasks",
        params={
            "q": "launch",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Rashed",
        },
    )

    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Plan launch"
    assert r.json()[0]["assignee"] == "Rashed"


def test_list_tasks_search_title_and_description_returns_matches(client):
    client.post(
        "/tasks",
        json={
            "title": "Launch plan",
            "description": "Gather feedback",
            "status": "ToDo",
            "priority": "Medium",
        },
    )

    client.post(
        "/tasks",
        json={
            "title": "Write notes",
            "description": "Review launch checklist",
            "status": "InProgress",
            "priority": "Low",
        },
    )

    r = client.get("/tasks", params={"q": "review"})

    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["title"] == "Write notes"
    assert r.json()[0]["description"] == "Review launch checklist"


def test_list_tasks_no_match_returns_200_and_empty_list(client):
    client.post(
        "/tasks",
        json={
            "title": "Existing task",
            "status": "ToDo",
            "priority": "Medium",
        },
    )

    r = client.get("/tasks", params={"q": "no-such-task"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_invalid_status_filter_returns_422(client):
    r = client.get("/tasks", params={"status": "Unknown"})

    assert r.status_code == 422
    assert "detail" in r.json()


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]

    r = client.get(f"/tasks/{task_id}")

    assert r.status_code == 200
    assert r.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    r = client.get("/tasks/not-found")

    assert r.status_code == 404
    assert r.json() == {
        "detail": "Task with id not-found not found"
    }


def test_patch_partial_update_keeps_other_fields(client):
    create = client.post(
        "/tasks",
        json={
            "title": "Original",
            "description": "Original description",
            "priority": "High",
        },
    )

    task = create.json()

    r = client.patch(
        f"/tasks/{task['id']}",
        json={"title": "Updated"},
    )

    assert r.status_code == 200

    data = r.json()
    assert data["title"] == "Updated"
    assert data["description"] == "Original description"
    assert data["priority"] == "High"


def test_patch_task_with_invalid_priority_value_returns_422(client):
    create = client.post(
        "/tasks",
        json={
            "title": "Task",
            "priority": "High",
        },
    )

    task = create.json()

    r = client.patch(
        f"/tasks/{task['id']}",
        json={"priority": "Urgent"},
    )

    assert r.status_code == 422
    assert "detail" in r.json()
    assert "priority" in str(r.json()["detail"])


def test_patch_not_found_returns_404(client):
    r = client.patch(
        "/tasks/not-found",
        json={"title": "Updated"},
    )

    assert r.status_code == 404
    assert r.json() == {
        "detail": "Task with id not-found not found"
    }


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "InProgress"},
    )

    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "Done"},
    )

    assert r.status_code == 422


def test_patch_same_status_returns_200(client, created_task):
    task_id = created_task["id"]

    r = client.patch(
        f"/tasks/{task_id}",
        json={"status": "ToDo"},
    )

    assert r.status_code == 200
    assert r.json()["status"] == "ToDo"


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]

    r = client.delete(f"/tasks/{task_id}")

    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/not-found")

    assert r.status_code == 404
    assert r.json() == {
        "detail": "Task with id not-found not found"
    }