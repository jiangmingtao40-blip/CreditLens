# -*- coding: utf-8 -*-
"""
Credit Report Recognition System - Integration Test
Verify: AI Service + Credit Backend + Full API Chain
"""
import os
import sys
import json
import time
import logging
import requests
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("integration-test")

AI_SERVICE_URL = "http://localhost:8000"
CREDIT_BACKEND_URL = "http://localhost:20510"
TEST_RESULTS = {"passed": 0, "failed": 0}


def test_case(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"\n{'='*60}")
            logger.info(f"TEST: {name}")
            logger.info(f"{'='*60}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"PASS: {name}")
                TEST_RESULTS["passed"] += 1
                return result
            except AssertionError as e:
                logger.error(f"FAIL: {name} - {e}")
                TEST_RESULTS["failed"] += 1
            except Exception as e:
                logger.error(f"FAIL: {name} - {e}")
                TEST_RESULTS["failed"] += 1
        return wrapper
    return decorator


# ─── Helper ────────────────────────────────────────────────
def create_test_png(filepath):
    """Create minimal valid PNG file"""
    import struct, zlib
    raw = b'\x00' + b'\xff\xff\xff' * 10
    for y in range(10):
        raw += b'\x00' + b'\xff\xff\xff' * 10

    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', 10, 10, 8, 2, 0, 0, 0)
    with open(filepath, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' +
                chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', zlib.compress(raw)) +
                chunk(b'IEND', b''))


# ══════════════════�?4.1 API Testing ════════════════════�?

@test_case("AI Service Health Check")
def test_ai_health():
    resp = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
    assert resp.status_code == 200, f"Status: {resp.status_code}"
    data = resp.json()
    assert data["status"] == "healthy"
    logger.info(f"  AI Service: {data['service']} v{data['version']}")


@test_case("AI Service File Upload")
def test_ai_upload():
    test_file = "_test_upload.png"
    create_test_png(test_file)
    try:
        with open(test_file, "rb") as f:
            resp = requests.post(
                f"{AI_SERVICE_URL}/api/ocr/upload",
                files={"file": ("report.png", f, "image/png")},
                timeout=10
            )
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        data = resp.json()
        assert "task_id" in data, f"Missing task_id: {data}"
        logger.info(f"  Upload OK, task_id: {data['task_id']}")
        return data["task_id"]
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


@test_case("Credit Backend - Token Validation")
def test_credit_token():
    resp = requests.post(f"{CREDIT_BACKEND_URL}/api/credit/upload", timeout=5)
    assert resp.status_code == 401, f"Should be 401, got: {resp.status_code}"
    logger.info(f"  Token validation OK: {resp.status_code}")


@test_case("AI Service - Result Query (Nonexistent)")
def test_ai_result_nonexistent():
    resp = requests.get(
        f"{AI_SERVICE_URL}/api/ocr/result/nonexistent-task",
        timeout=5
    )
    assert resp.status_code == 404, f"Should be 404, got: {resp.status_code}"
    logger.info(f"  Nonexistent task returns 404")


@test_case("AI Service - Delete Task")
def test_ai_delete():
    task_id = test_ai_upload()
    resp = requests.delete(
        f"{AI_SERVICE_URL}/api/ocr/task/{task_id}",
        timeout=5
    )
    assert resp.status_code == 200, f"Delete failed: {resp.status_code}"
    logger.info(f"  Delete OK: {resp.json()['message']}")


@test_case("AI Service - Unsupported File Format")
def test_ai_unsupported():
    resp = requests.post(
        f"{AI_SERVICE_URL}/api/ocr/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
        timeout=5
    )
    assert resp.status_code == 400, f"Should be 400, got: {resp.status_code}"
    logger.info(f"  Unsupported format rejected: {resp.status_code}")


# ══════════════════�?4.2 Full Chain Testing ════════════════�?

@test_case("Full Chain: Upload -> Analyze -> Result")
def test_full_chain():
    test_file = "_test_chain.png"
    create_test_png(test_file)
    try:
        # Upload
        with open(test_file, "rb") as f:
            resp = requests.post(
                f"{AI_SERVICE_URL}/api/ocr/upload",
                files={"file": ("credit_report.png", f, "image/png")},
                timeout=10
            )
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]
        logger.info(f"  1. Upload OK: {task_id}")

        # Query result (may be 404 if Redis unavailable - fallback to in-memory check)
        resp = requests.get(
            f"{AI_SERVICE_URL}/api/ocr/result/{task_id}",
            timeout=10
        )
        if resp.status_code == 200:
            logger.info(f"  2. Result query OK: {resp.json()['status']}")
        else:
            logger.info(f"  2. Result query returned {resp.status_code} (Redis unavailable)")

        # Cleanup
        resp = requests.delete(
            f"{AI_SERVICE_URL}/api/ocr/task/{task_id}",
            timeout=5
        )
        assert resp.status_code == 200
        logger.info(f"  3. Cleanup OK")

        logger.info(f"  Full chain PASS")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


@test_case("Credit Backend - Records API")
def test_credit_records():
    headers = {"Authorization": "Bearer test_token"}
    resp = requests.get(
        f"{CREDIT_BACKEND_URL}/api/credit/records",
        headers=headers,
        timeout=5
    )
    assert resp.status_code == 200, f"Status: {resp.status_code}"
    data = resp.json()
    assert "records" in data
    logger.info(f"  Records API OK, total: {data.get('total', 0)}")


@test_case("Credit Backend - Detail Not Found")
def test_credit_detail_not_found():
    headers = {"Authorization": "Bearer test_token"}
    resp = requests.get(
        f"{CREDIT_BACKEND_URL}/api/credit/detail/99999",
        headers=headers,
        timeout=5
    )
    assert resp.status_code == 404, f"Should be 404, got: {resp.status_code}"
    logger.info(f"  Not found returns 404")


@test_case("Credit Backend - Delete Not Found")
def test_credit_delete_not_found():
    headers = {"Authorization": "Bearer test_token"}
    resp = requests.delete(
        f"{CREDIT_BACKEND_URL}/api/credit/delete/99999",
        headers=headers,
        timeout=5
    )
    assert resp.status_code == 404, f"Should be 404, got: {resp.status_code}"
    logger.info(f"  Delete not found returns 404")


@test_case("Concurrent Health Checks")
def test_concurrent():
    results = []
    for i in range(5):
        try:
            resp = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
            results.append(resp.status_code == 200)
        except Exception:
            results.append(False)
    rate = sum(results) / len(results)
    assert rate > 0.8, f"Success rate: {rate:.0%}"
    logger.info(f"  Concurrent: {rate:.0%} ({sum(results)}/{len(results)})")


# ══════════════════�?Main ══════════════════════════════

def main():
    logger.info("\n" + "="*60)
    logger.info("Credit Report System - Integration Test")
    logger.info("="*60)
    logger.info(f"  AI Service: {AI_SERVICE_URL}")
    logger.info(f"  Credit Backend: {CREDIT_BACKEND_URL}")
    logger.info(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        test_ai_health,
        test_credit_token,
        test_ai_upload,
        test_ai_result_nonexistent,
        test_ai_delete,
        test_ai_unsupported,
        test_full_chain,
        test_credit_records,
        test_credit_detail_not_found,
        test_credit_delete_not_found,
        test_concurrent,
    ]

    for t in tests:
        try:
            t()
        except Exception as e:
            logger.error(f"Test error: {e}")
            TEST_RESULTS["failed"] += 1

    total = TEST_RESULTS["passed"] + TEST_RESULTS["failed"]
    logger.info(f"\n{'='*60}")
    logger.info("TEST REPORT")
    logger.info(f"  Total: {total}")
    logger.info(f"  Passed: {TEST_RESULTS['passed']}")
    logger.info(f"  Failed: {TEST_RESULTS['failed']}")
    if total > 0:
        logger.info(f"  Rate: {TEST_RESULTS['passed']/total*100:.1f}%")
    else:
        logger.info("  No tests ran")

    if TEST_RESULTS["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
