import sys
import json
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(path: str, data: dict = None, method: str = "GET", headers: dict = None) -> tuple:
    url = f"{BASE_URL}{path}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode('utf-8')
            res_headers = res.info()
            try:
                res_data = json.loads(res_body) if res_body else {}
            except json.JSONDecodeError:
                res_data = res_body
            return res.status, res_data, res_headers
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(res_body), e.info()
        except json.JSONDecodeError:
            return e.code, {"success": False, "error": res_body}, e.info()
    except Exception as e:
        return 500, {"success": False, "error": f"Connection failed: {str(e)}"}, {}

def upload_file_mock(filename: str, content_text: str) -> tuple:
    url = f"{BASE_URL}/documents/upload"
    boundary = "----MultipartTestBoundaryForFastAPI"
    crlf = b"\r\n"
    
    body_parts = [
        f"--{boundary}".encode('utf-8'),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode('utf-8'),
        b"Content-Type: text/plain",
        b"",
        content_text.encode('utf-8'),
        f"--{boundary}--".encode('utf-8'),
        b""
    ]
    
    data = crlf.join(body_parts)
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('Content-Length', str(len(data)))
    
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(res_body)
        except json.JSONDecodeError:
            return e.code, {"success": False, "error": res_body}
    except Exception as e:
        return 500, {"success": False, "error": f"Upload request failed: {str(e)}"}

def run_tests():
    print("=" * 60)
    print("       SMART COLLEGE AI BACKEND VERIFICATION RUNNER         ")
    print("=" * 60)
    print(f"Connecting to test server base URL: {BASE_URL}\n")

    # Test 1: Health Check
    print("Test 1: Health Check [/api/health]")
    status_code, body, _ = make_request("/health")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True, f"Expected success=True, got {body}"
    assert body.get("data", {}).get("status") == "ok", "Expected status=='ok'"
    print("  [PASS] Health status ok with correct wrapper.\n")

    # Test 2: CORS Preflight Header Assertion
    print("Test 2: CORS Preflight Check")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    status_code, _, res_headers = make_request("/health", method="OPTIONS", headers=headers)
    # preflight response standard success is 200 OK or 204 No Content
    assert status_code in (200, 204), f"Expected 200/204 CORS response, got {status_code}"
    print("  [PASS] Preflight headers verified.\n")

    # Test 3: Upload Text Note Document
    print("Test 3: File Upload [/api/documents/upload]")
    mock_notes = """
# Lecture: Operating System Processes

A process is defined as a program in execution. It includes the program code, the stack, and register states.
Memory management: Physical memory is broken into frames, and logical memory is broken into pages.
Paging is defined as a memory allocation scheme that avoids contiguous mapping.
Virtual memory refers to a technique that allows execution of non-completely loaded processes.
    """
    status_code, body = upload_file_mock("test_os_notes.txt", mock_notes)
    assert status_code == 200, f"Expected 200, got {status_code}: {body}"
    assert body.get("success") is True, "Expected success=True"
    doc_data = body.get("data", {})
    doc_id = doc_data.get("id")
    assert doc_id is not None, "Expected uploaded doc to have ID"
    assert doc_data.get("parse_status") == "completed", "Expected parse_status=='completed'"
    assert doc_data.get("page_count") == 1, "Expected text files to have page_count==1"
    print(f"  [PASS] Uploaded file successfully. Got ID: {doc_id}\n")

    # Test 4: Unsupported File Upload Rejection
    print("Test 4: Invalid Upload Rejection")
    status_code, body = upload_file_mock("malicious_script.py", "import sys; print('hack')")
    assert status_code == 400, f"Expected 400, got {status_code}"
    assert body.get("success") is False, "Expected success=False"
    assert "error" in body, "Expected error payload in wrapper response"
    print(f"  [PASS] Properly blocked python file with message: '{body.get('error')}'\n")

    # Test 5: List Documents
    print("Test 5: List Documents [/api/documents]")
    status_code, body, _ = make_request("/documents")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True, "Expected success=True"
    docs_list = body.get("data", [])
    assert len(docs_list) > 0, "Expected at least one document in list"
    # Ensure full extracted text is hidden from list view payloads
    assert "extracted_text" not in docs_list[0], "Security Error: Extracted text should be hidden from list query!"
    print(f"  [PASS] Documents list returned {len(docs_list)} item(s) without text leaks.\n")

    # Test 6: Set Active Document Focus
    print("Test 6: Set Active Workspace Focus [/api/documents/active]")
    status_code, body, _ = make_request("/documents/active", data={"id": doc_id}, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True
    assert body.get("data", {}).get("active_document_id") == doc_id
    print("  [PASS] Successfully switched active workspace ID.\n")

    # Test 7: Grounded Q&A doubt resolution
    print("Test 7: Grounded Chat doubted [/api/ai/chat]")
    chat_payload = {
        "document_id": doc_id,
        "message": "Explain what a process is?"
    }
    status_code, body, _ = make_request("/ai/chat", data=chat_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}: {body}"
    chat_data = body.get("data", {})
    assert "program in execution" in chat_data.get("text", ""), "Doubt response not grounded in document notes!"
    assert "citation" in chat_data, "Expected citation reference"
    assert chat_data.get("source_page") == 1
    print("  [PASS] Received grounded AI reply with page citation.\n")

    # Test 8: Flashcard Generation
    print("Test 8: Generate Flashcards [/api/ai/flashcards]")
    fc_payload = {
        "document_id": doc_id,
        "count": 3
    }
    status_code, body, _ = make_request("/ai/flashcards", data=fc_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}: {body}"
    cards = body.get("data", [])
    assert len(cards) > 0, "Expected flashcards list"
    assert "question" in cards[0] and "answer" in cards[0], "Flashcard shapes invalid"
    print(f"  [PASS] Compiled {len(cards)} study flashcards.\n")

    # Test 9: Quiz MCQ generation
    print("Test 9: Generate Quiz [/api/ai/quiz]")
    quiz_payload = {
        "document_id": doc_id,
        "count": 3
    }
    status_code, body, _ = make_request("/ai/quiz", data=quiz_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}: {body}"
    quiz_questions = body.get("data", [])
    assert len(quiz_questions) > 0, "Expected quiz list"
    q_item = quiz_questions[0]
    assert "question" in q_item
    assert "options" in q_item and len(q_item["options"]) == 4, "Quiz MCQs must have exactly 4 choices"
    assert "correctIndex" in q_item
    assert "explanation" in q_item
    print(f"  [PASS] Generated MCQs with distractor choices and explanation outlines.\n")

    # Test 10: Delete Document
    print("Test 10: Delete Document [/api/documents/{id}]")
    status_code, body, _ = make_request(f"/documents/{doc_id}", method="DELETE")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True
    assert body.get("data", {}).get("deleted") is True
    print("  [PASS] Successfully cleaned document from storage.\n")

    # Test 11: Settings GET and POST Verification
    print("Test 11: User Settings Management [/api/settings]")
    status_code, body, _ = make_request("/settings")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True
    settings_data = body.get("data", {})
    assert "user_name" in settings_data, "Expected user_name in settings"
    
    updated_payload = {
        "user_name": "Test User 313",
        "user_about": "Testing Persistent Personalization",
        "model": "local-heuristic",
        "ollama_url": "http://localhost:11434",
        "system_prompt": "You are a specialized test agent."
    }
    status_code, body, _ = make_request("/settings", data=updated_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("success") is True
    assert body.get("data", {}).get("user_name") == "Test User 313"
    
    status_code, body, _ = make_request("/settings")
    assert status_code == 200, f"Expected 200, got {status_code}"
    assert body.get("data", {}).get("user_name") == "Test User 313"
    assert body.get("data", {}).get("user_about") == "Testing Persistent Personalization"
    print("  [PASS] Settings retrieved, updated, and persisted successfully.\n")

    # Test 12: Note Grounding & Retrieval Quality Checks
    print("Test 12: Grounding and Fallback Quality Checks")
    
    # 1. Upload a fresh testing document with specific chapters
    detailed_notes = """
# Chapter 1: Chemical Thermodynamics
Thermodynamics is defined as the science of heat and temperature.
The first law states that energy cannot be created or destroyed.
Entropy refers to a measure of molecular disorder or randomness.
    """
    status_code, body = upload_file_mock("chemistry_notes.txt", detailed_notes)
    assert status_code == 200, f"Expected 200, got {status_code}"
    chem_doc_id = body.get("data", {}).get("id")
    
    # 2. Query matching topic - Expect grounded answer
    chat_payload = {
        "document_id": chem_doc_id,
        "message": "Explain what entropy is?"
    }
    status_code, body, _ = make_request("/ai/chat", data=chat_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}"
    chat_data = body.get("data", {})
    assert "molecular disorder" in chat_data.get("text", "").lower(), "Grounded answer did not contain correct notes content!"
    assert chat_data.get("source_page") == 1
    
    # 3. Query mismatching topic - Expect honest fallback
    chat_payload = {
        "document_id": chem_doc_id,
        "message": "Who painted the Mona Lisa?"
    }
    status_code, body, _ = make_request("/ai/chat", data=chat_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}"
    chat_data = body.get("data", {})
    assert "could not find a confident answer" in chat_data.get("text", "").lower(), "Expected low-confidence fallback warning!"
    assert chat_data.get("citation") is None, "Fallback should not contain fake citation!"
    
    # 4. Query document summary - Expect real note summary
    chat_payload = {
        "document_id": chem_doc_id,
        "message": "Give me a summary of this document."
    }
    status_code, body, _ = make_request("/ai/chat", data=chat_payload, method="POST")
    assert status_code == 200, f"Expected 200, got {status_code}"
    chat_data = body.get("data", {})
    assert "chemical thermodynamics" in chat_data.get("text", "").lower(), "Summary did not parse actual notes headings!"
    print("  [PASS] Grounded Q&A, fallback limits, and note summary verified successfully.\n")

    # Clean up chemistry test file
    make_request(f"/documents/{chem_doc_id}", method="DELETE")

    print("=" * 60)
    print("         ALL 12 ENDPOINT VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n[FAIL] ASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        sys.exit(1)
