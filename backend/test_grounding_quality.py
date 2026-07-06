import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(path: str, data: dict = None, method: str = "GET"):
    url = f"{BASE_URL}{path}"
    req_data = None
    headers = {}
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body
    except Exception as e:
        return 500, {"success": False, "error": str(e)}

def upload_mock_file(filename: str, content: str):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
        f"{content}\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    
    url = f"{BASE_URL}/documents/upload"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))

def run_quality_check():
    print("=" * 70)
    print("       SMART COLLEGE AI - GROUNDING & INTEGRATION VERIFIER")
    print("=" * 70)

    # 1. Upload Doc A: Biology Notes (expanded to provide enough grounded chunks)
    print("\n1. Uploading Document A: biology_notes.txt...")
    bio_content = """# Chapter 1: Cell Biology
Cells are the basic structural and functional units of all living organisms.
The cell membrane controls the movement of substances in and out of cells.

--- PAGE_BREAK ---

# Chapter 2: Energy production
Mitochondria are the powerhouse of the cell, generating adenosine triphosphate (ATP) through cellular respiration.
Chloroplasts perform photosynthesis in plant cells to generate glucose.

--- PAGE_BREAK ---

# Chapter 3: Cellular division
Mitosis is a process of cell duplication, or reproduction, during which one cell gives rise to two genetically identical daughter cells.
Meiosis is a division process that reduces the chromosome number by half."""
    status, res_a = upload_mock_file("biology_notes.txt", bio_content)
    assert status == 200, f"Failed to upload A: {res_a}"
    doc_a_id = res_a["data"]["id"]
    print(f"  [UPLOAD SUCCESS] Document A ID: {doc_a_id}")

    # 2. Upload Doc B: French Revolution Notes (expanded to provide enough grounded chunks)
    print("\n2. Uploading Document B: history_notes.txt...")
    hist_content = """# Chapter 1: The French Revolution
The French Revolution began in 1789 with the storming of the Bastille.
King Louis XVI was executed in 1793 by guillotine.

--- PAGE_BREAK ---

# Chapter 2: The Reign of Terror
The Reign of Terror was led by Maximilien Robespierre, who executed thousands of political opponents.
The Jacobins were the radical political faction that dominated the government.

--- PAGE_BREAK ---

# Chapter 3: Napoleon Bonaparte
Napoleon rose to power in the late stages of the revolution, eventually crowning himself Emperor of the French.
His code remains the basis of civil law in many countries today."""
    status, res_b = upload_mock_file("history_notes.txt", hist_content)
    assert status == 200, f"Failed to upload B: {res_b}"
    doc_b_id = res_b["data"]["id"]
    print(f"  [UPLOAD SUCCESS] Document B ID: {doc_b_id}")

    # 3. Test Doc A QA
    print("\n3. Activating Document A context via POST /api/documents/active...")
    status, active_res = make_request("/documents/active", data={"id": doc_a_id}, method="POST")
    assert status == 200 and active_res["data"]["active_document_id"] == doc_a_id
    
    print("\n4. Requesting Document A Summary (Q: 'What is this document about?')...")
    status, chat_a_sum = make_request("/ai/chat", data={"document_id": doc_a_id, "message": "what is this document about?"}, method="POST")
    assert status == 200
    text_a = chat_a_sum["data"]["text"]
    citation_a = chat_a_sum["data"]["citation"]
    print(f"  [RESPONSE PAYLOAD]:\n    Text: {text_a[:140]}...\n    Citation: {citation_a}")
    assert "cell biology" in text_a.lower(), "Summary of A did not contain cell biology content!"
    assert citation_a == f"Overview (biology_notes.txt)", f"Unexpected citation: {citation_a}"

    print("\n5. Asking specific concept question on Document A (Q: 'What controls substances in cells?')...")
    status, chat_a_q = make_request("/ai/chat", data={"document_id": doc_a_id, "message": "What controls substances in cells?"}, method="POST")
    assert status == 200
    text_aq = chat_a_q["data"]["text"]
    citation_aq = chat_a_q["data"]["citation"]
    print(f"  [RESPONSE PAYLOAD]:\n    Text: {text_aq}\n    Citation: {citation_aq}")
    assert "cell membrane" in text_aq.lower(), "Answer did not retrieve the cell membrane detail!"
    assert citation_aq == f"Page 1 (biology_notes.txt)", f"Unexpected citation: {citation_aq}"

    # 4. Test Doc B QA
    print("\n6. Activating Document B context via POST /api/documents/active...")
    status, active_res = make_request("/documents/active", data={"id": doc_b_id}, method="POST")
    assert status == 200 and active_res["data"]["active_document_id"] == doc_b_id

    print("\n7. Requesting Document B Summary (Q: 'What is this document about?')...")
    status, chat_b_sum = make_request("/ai/chat", data={"document_id": doc_b_id, "message": "what is this document about?"}, method="POST")
    assert status == 200
    text_b = chat_b_sum["data"]["text"]
    citation_b = chat_b_sum["data"]["citation"]
    print(f"  [RESPONSE PAYLOAD]:\n    Text: {text_b[:140]}...\n    Citation: {citation_b}")
    assert "french revolution" in text_b.lower(), "Summary of B did not contain french revolution content!"
    assert citation_b == f"Overview (history_notes.txt)", f"Unexpected citation: {citation_b}"

    print("\n8. Asking specific concept question on Document B (Q: 'Who led the Reign of Terror?')...")
    status, chat_b_q = make_request("/ai/chat", data={"document_id": doc_b_id, "message": "Who led the Reign of Terror?"}, method="POST")
    assert status == 200
    text_bq = chat_b_q["data"]["text"]
    citation_bq = chat_b_q["data"]["citation"]
    print(f"  [RESPONSE PAYLOAD]:\n    Text: {text_bq}\n    Citation: {citation_bq}")
    assert "robespierre" in text_bq.lower(), "Answer did not retrieve Robespierre detail!"
    assert citation_bq == f"Page 2 (history_notes.txt)", f"Unexpected citation: {citation_bq}"

    # 5. Verify Isolation (Answers differ)
    print("\n9. Verifying content-based isolation between A and B...")
    assert text_a != text_b, "Summaries are template-identical!"
    assert text_aq != text_bq, "Concept answers are template-identical!"
    print("  [PASS] Isolation verified. Summaries and concept answers differ entirely based on document content.")

    # 6. Generate Flashcards for Doc A
    print("\n10. Compiling Flashcards for Document A (Count: 3)...")
    status, fc_res = make_request("/ai/flashcards", data={"document_id": doc_a_id, "count": 3}, method="POST")
    assert status == 200
    cards = fc_res["data"]
    print(f"  [RESPONSE SUMMARY]: Count={len(cards)}")
    for card in cards:
        print(f"    - Q: {card['question']}\n      A: {card['answer']}")
        assert any(x in card["question"].lower() or x in card["answer"].lower() for x in ["cell", "mitochondria", "membrane", "mitosis", "meiosis", "chloroplasts"]), "Flashcard content not grounded in Document A!"

    # 7. Generate Quiz for Doc B
    print("\n11. Compiling Practice Quiz for Document B (Count: 3)...")
    status, qz_res = make_request("/ai/quiz", data={"document_id": doc_b_id, "count": 3}, method="POST")
    assert status == 200
    questions = qz_res["data"]
    print(f"  [RESPONSE SUMMARY]: Count={len(questions)}")
    for q in questions:
        print(f"    - Q: {q['question']}\n      Choices: {q['options']}\n      Correct: Option {q['correctIndex']}\n      Expl: {q['explanation']}")
        assert any(x in q["question"].lower() or x in q["explanation"].lower() for x in ["bastille", "louis", "robespierre", "terror", "napoleon", "jacobins"]), "Quiz content not grounded in Document B!"

    # 8. Check Citation Guardrails (Off-topic query fallback)
    print("\n12. Querying off-topic question to Doc B (Q: 'Who painted the Mona Lisa?')...")
    status, chat_err = make_request("/ai/chat", data={"document_id": doc_b_id, "message": "Who painted the Mona Lisa?"}, method="POST")
    assert status == 200
    err_text = chat_err["data"]["text"]
    err_citation = chat_err["data"]["citation"]
    print(f"  [RESPONSE PAYLOAD]:\n    Text: {err_text}\n    Citation: {err_citation}")
    assert "could not find a confident answer" in err_text.lower(), "Incorrect fallback answer!"
    assert err_citation is None, "Fallback answer should have a null/None citation!"
    print("  [PASS] Quality guardrails confirmed. No hallucinated citations returned.")

    # Clean up files
    print("\n13. Cleaning up temporary verification files...")
    make_request(f"/documents/{doc_a_id}", method="DELETE")
    make_request(f"/documents/{doc_b_id}", method="DELETE")
    print("  [CLEANUP SUCCESS]")
    
    print("\n" + "=" * 70)
    print("      ALL END-TO-END QUALITY VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_quality_check()
    except AssertionError as e:
        print(f"\n[FAIL] QUALITY CHECK FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        sys.exit(1)
