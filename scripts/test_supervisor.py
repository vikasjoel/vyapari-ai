"""Quick local test of the supervisor agent."""

import sys
sys.path.insert(0, ".")

from agents.supervisor import create_supervisor_agent


def test_supervisor():
    print("Creating supervisor agent...")
    agent = create_supervisor_agent()

    print("\n--- Test 1: Hindi greeting ---")
    result = agent("Namaste, mera naam Ramesh hai")
    print(f"Response: {result.message}")

    print("\n--- Test 2: Follow-up (shop info) ---")
    result = agent("Delhi mein kirana store hai mera")
    print(f"Response: {result.message}")

    print("\n--- Test 3: English fallback ---")
    agent2 = create_supervisor_agent()
    result = agent2("Hi, I want to list my shop on ONDC")
    print(f"Response: {result.message}")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_supervisor()
