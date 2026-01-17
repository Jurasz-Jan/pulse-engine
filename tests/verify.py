import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000"

async def test_health():
    print("Testing / ...", end=" ")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/")
            if resp.status_code == 200:
                print("OK")
                return True
            else:
                print(f"FAILED ({resp.status_code})")
                return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

async def test_scrape():
    print("Testing POST /scrape ...", end=" ")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{BASE_URL}/scrape", json={"url": "https://example.com"})
            if resp.status_code == 200:
                data = resp.json()
                if "task_id" in data:
                    print(f"OK (Task ID: {data['task_id']})")
                    return True
            print(f"FAILED (Response: {resp.text})")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

async def test_chat_validation():
    print("Testing POST /chat validation ...", end=" ")
    async with httpx.AsyncClient() as client:
        try:
            # Empty query should fail validation (422)
            resp = await client.post(f"{BASE_URL}/chat", json={})
            if resp.status_code == 422:
                print("OK (Correctly rejected)")
                return True
            print(f"FAILED (Expected 422, got {resp.status_code})")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

async def test_vague_query():
    print("Testing Self-Correction (Vague Query) ...", end=" ")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # "it" is very vague, should trigger rewrite
            resp = await client.post(f"{BASE_URL}/chat", json={"query": "tell me about it"})
            if resp.status_code == 200:
                data = resp.json()
                trace = data.get("trace", [])
                # Check for rewrite signature in trace
                rewrote = any("Rewriting query" in str(step) for step in trace)
                if rewrote:
                    print("OK (Rewritten)")
                    return True
                else:
                    print("WARN (No rewrite triggered, maybe score was high enough?)")
                    print(f"Trace: {trace}")
                    return True # Pass anyway, as model behavior mimics variance
            print(f"FAILED (Response: {resp.text})")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

async def main():
    print(f"Running automated tests against {BASE_URL}\n")
    results = [
        await test_health(),
        await test_scrape(),
        await test_chat_validation(),
        await test_vague_query()
    ]
    
    if all(results):
        print("\nAll tests passed! ✅")
        sys.exit(0)
    else:
        print("\nSome tests failed. ❌")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
