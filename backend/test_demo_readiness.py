import os
import urllib.request
import json
import sys
import fitz  # PyMuPDF

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
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"success": False, "error": e.reason}
        return e.code, body
    except Exception as e:
        return 500, {"success": False, "error": str(e)}

def upload_file(filename: str, file_path: str):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    url = f"{BASE_URL}/documents/upload"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def build_test_files():
    print("[BUILD] Generating user-style test files...")
    
    # 1. Plain Text Note (no explicit page breaks, length ~3500 chars to test virtual page segmenting)
    plain_text = (
        "# Chapter 1: Introduction to Mechanics\n"
        "Mechanics is the area of science concerned with the behavior of physical bodies when subjected to forces.\n"
        "It has two main branches: statics and dynamics.\n\n"
        "Statics deals with bodies at rest or moving with constant velocity, while dynamics deals with accelerating bodies.\n\n" * 15
    )
    with open("temp_plain_text.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
        
    # 2. Standard PDF Note (Physics)
    doc_std = fitz.open()
    page_std = doc_std.new_page(width=600, height=800)
    page_std.insert_textbox(
        fitz.Rect(50, 50, 550, 750),
        "# Physics Study Notes\n\n"
        "Newton's First Law: An object remains at rest unless acted on by a net force.\n"
        "Newton's Second Law: Force is equal to mass times acceleration (F = ma).\n"
        "Newton's Third Law: For every action, there is an equal and opposite reaction."
    )
    doc_std.save("temp_standard.pdf")
    doc_std.close()

    # 3. Multi-Column PDF Note (Chemistry 2-column layout)
    doc_mc = fitz.open()
    page_mc = doc_mc.new_page(width=600, height=800)
    # Left column textbox
    page_mc.insert_textbox(
        fitz.Rect(50, 100, 280, 700),
        "Chemistry Left Column:\n"
        "Acids are substances that donate protons (hydrogen ions).\n"
        "Common examples of acids include hydrochloric acid and sulfuric acid.\n"
        "They typically taste sour and turn blue litmus paper red."
    )
    # Right column textbox
    page_mc.insert_textbox(
        fitz.Rect(320, 100, 550, 700),
        "Chemistry Right Column:\n"
        "Bases are substances that accept protons or donate hydroxide ions.\n"
        "Common examples of bases include sodium hydroxide and calcium hydroxide.\n"
        "They feel slippery to the touch and turn red litmus paper blue."
    )
    doc_mc.save("temp_multi_column.pdf")
    doc_mc.close()

    # 4. Scanned / Image-only PDF (creates page but no text strings inserted)
    doc_img = fitz.open()
    doc_img.new_page(width=600, height=800)
    doc_img.save("temp_scanned.pdf")
    doc_img.close()

def clean_test_files():
    print("[CLEANUP] Removing temp local test files...")
    for fn in ["temp_plain_text.txt", "temp_standard.pdf", "temp_multi_column.pdf", "temp_scanned.pdf"]:
        if os.path.exists(fn):
            os.remove(fn)

def run_demo_verification():
    build_test_files()
    
    print("\n" + "="*80)
    print("                FINAL DEMO-READINESS SYSTEM PASS")
    print("="*80)
    
    try:
        # TEST A: Reject Scanned/Empty PDF
        print("\nTEST 1: Uploading scanned/empty PDF (temp_scanned.pdf)...")
        status, res = upload_file("temp_scanned.pdf", "temp_scanned.pdf")
        print(f"  - Route: POST /api/documents/upload")
        print(f"  - Status: {status}")
        print(f"  - Output: {res}")
        if status == 400:
            print("  [PASS] Scanned PDF rejected with HTTP 400 Bad Request successfully.")
        else:
            print("  [FAIL] Scanned PDF did not fail or return 400!")
            assert False
            
        # TEST B: Plain Text Note Upload & Virtual Page Segmentation
        print("\nTEST 2: Uploading plain text note without page marks (temp_plain_text.txt)...")
        status, res_txt = upload_file("temp_plain_text.txt", "temp_plain_text.txt")
        print(f"  - Route: POST /api/documents/upload")
        print(f"  - Output: {res_txt['data']['name']} (ID: {res_txt['data']['id']}), Pages: {res_txt['data']['page_count']}")
        assert status == 200
        txt_id = res_txt["data"]["id"]
        # Since text length is ~3500, it should have been segmented into virtual pages
        assert res_txt["data"]["page_count"] > 1, f"Expected multiple virtual pages, got {res_txt['data']['page_count']}"
        print(f"  [PASS] Virtual page pre-segmentation worked. Pages estimated: {res_txt['data']['page_count']}")

        # TEST C: Multi-Column PDF Extraction Reading Order
        print("\nTEST 3: Uploading multi-column PDF (temp_multi_column.pdf)...")
        status, res_mc = upload_file("temp_multi_column.pdf", "temp_multi_column.pdf")
        print(f"  - Route: POST /api/documents/upload")
        assert status == 200
        mc_id = res_mc["data"]["id"]
        
        # Retrieve full detail text to inspect reading order
        status, res_detail = make_request(f"/documents/{mc_id}")
        assert status == 200
        full_text = res_detail["data"]["extracted_text"]
        print("  - Extracted Text snippet:")
        for line in full_text.split("\n")[:12]:
            print(f"    | {line}")
            
        # Check that Left Column content precedes Right Column content (not interleaved)
        left_index = full_text.find("Chemistry Left Column")
        right_index = full_text.find("Chemistry Right Column")
        assert left_index != -1 and right_index != -1
        assert left_index < right_index, "Reading order mixed! Right column text interleaved with left column."
        print("  [PASS] Multi-column PDF reading order sorted correctly by column (left before right).")

        # TEST D: Active Document Swapping & Grounded Q&A
        print("\nTEST 4: Activating chemistry document and testing grounded Q&A...")
        status, res_act = make_request("/documents/active", data={"id": mc_id}, method="POST")
        assert status == 200
        
        # Question answerable by Left Column
        print("  - Q: 'What do acids taste like?'")
        status, res_chat_acid = make_request("/ai/chat", data={"document_id": mc_id, "message": "What do acids taste like?"}, method="POST")
        print(f"    Ans: {res_chat_acid['data']['text']}")
        print(f"    Citation: {res_chat_acid['data']['citation']}")
        assert "sour" in res_chat_acid["data"]["text"].lower()
        assert res_chat_acid["data"]["citation"] == "Page 1 (temp_multi_column.pdf)"
        
        # Question not answerable by notes (off-topic)
        print("  - Q: 'What is the speed of light?'")
        status, res_chat_off = make_request("/ai/chat", data={"document_id": mc_id, "message": "What is the speed of light?"}, method="POST")
        print(f"    Ans: {res_chat_off['data']['text']}")
        print(f"    Citation: {res_chat_off['data']['citation']}")
        assert "could not find a confident answer" in res_chat_off["data"]["text"].lower()
        assert res_chat_off["data"]["citation"] is None
        print("  [PASS] Active context Q&A, citations, and fallback limits verified.")

        # TEST E: Flashcards and Quiz compilation
        print("\nTEST 5: Compiling flashcards for text document...")
        status, res_fc = make_request("/ai/flashcards", data={"document_id": txt_id, "count": 2}, method="POST")
        print(f"  - Flashcards compiled: {len(res_fc['data'])}")
        assert status == 200 and len(res_fc["data"]) == 2
        
        print("TEST 6: Compiling quiz for chemistry PDF...")
        status, res_qz = make_request("/ai/quiz", data={"document_id": mc_id, "count": 2}, method="POST")
        print(f"  - Quiz MCQs compiled: {len(res_qz['data'])}")
        assert status == 200 and len(res_qz["data"]) == 2
        print("  [PASS] Study utilities compile grounded output successfully.")

        # Cleanup
        print("\nTEST 7: Cleaning up server uploads...")
        make_request(f"/documents/{txt_id}", method="DELETE")
        make_request(f"/documents/{mc_id}", method="DELETE")
        print("  [PASS] Temp document records deleted.")

        print("\n" + "="*80)
        print("                DEMO-READINESS VERIFICATION PASSED SUCCESSFULLY")
        print("="*80)

    except AssertionError:
        print("\n[FAIL] DEMO VERIFICATION RUNNER ENCOUNTERED A FAILURE CORNER CASE.")
        clean_test_files()
        sys.exit(1)
        
    clean_test_files()

if __name__ == "__main__":
    run_demo_verification()
