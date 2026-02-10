import io
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_submit_job_and_upload_resume(monkeypatch):
    job = {"job_description": "We need a Python FastAPI engineer with AI experience."}
    r = client.post("/submit-job", json=job)
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    file = io.BytesIO(pdf_bytes)
    r2 = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", file, "application/pdf")},
    )
    assert r2.status_code in (201, 422)
    if r2.status_code == 201:
        resume_id = r2.json()["resume_id"]
        r3 = client.post(
            "/tailor",
            json={"resume_id": resume_id, "job_id": job_id},
        )
        assert r3.status_code == 200
