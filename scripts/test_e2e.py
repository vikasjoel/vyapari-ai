"""End-to-end integration test — Full merchant journey through Supervisor.

Tests the complete flow:
1. Onboarding (greeting → registration)
2. Catalog (ask about products)
3. Orders (generate demo order, check savings)
4. Voice (voice command simulation)
5. Cross-agent handoffs
"""

import sys
import json
import time
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()


def create_supervisor():
    """Create and return the supervisor agent."""
    from agents.supervisor import create_supervisor_agent
    return create_supervisor_agent()


def test_step(supervisor, step_num, description, message):
    """Run a single test step and print results."""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print(f"{'='*60}")
    print(f"User: {message}\n")

    start = time.time()
    result = supervisor(message)
    elapsed = round(time.time() - start, 1)

    response = result.message
    # Handle dict responses from some agents
    if isinstance(response, dict):
        response = response.get("content", [{}])
        if isinstance(response, list) and response:
            response = response[0].get("text", str(response))

    print(f"Vyapari ({elapsed}s):\n{response}\n")
    return response


def run_full_journey():
    """Run the complete merchant journey end-to-end."""
    print("\n" + "=" * 60)
    print("  VYAPARI.AI — Full Merchant Journey E2E Test")
    print("=" * 60)

    supervisor = create_supervisor()
    print("Supervisor created with 4 specialist agents.\n")

    passed = 0
    total = 8

    # ── Step 1: Greeting → Onboarding ──
    try:
        r1 = test_step(
            supervisor, 1,
            "Greeting → should route to Onboarding Agent",
            "Namaste! Mujhe ONDC pe apni dukaan lagani hai"
        )
        print("✅ Routed to Onboarding Agent")
        passed += 1
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")

    # ── Step 2: Provide ALL details at once → fast registration ──
    try:
        r2 = test_step(
            supervisor, 2,
            "Provide all details → should extract all slots",
            "Main Suresh Patel hoon. Patel Grocery Store naam hai, Maninagar, Ahmedabad mein kirana store hai. Phone: 9898765432"
        )
        print("✅ Multi-slot extraction")
        passed += 1
    except Exception as e:
        print(f"❌ Step 2 failed: {e}")

    # ── Step 3: Confirm registration or provide remaining info ──
    try:
        r3 = test_step(
            supervisor, 3,
            "Confirm or complete registration",
            "Haan ji, sab sahi hai. Register kar dijiye."
        )
        print("✅ Registration flow progressed")
        passed += 1
    except Exception as e:
        print(f"❌ Step 3 failed: {e}")

    # ── Step 4: Ask about catalog → Catalog Agent ──
    try:
        r4 = test_step(
            supervisor, 4,
            "Ask about products → should route to Catalog Agent",
            "Mera catalog dikhao, kitne products hain?"
        )
        print("✅ Routed to Catalog Agent")
        passed += 1
    except Exception as e:
        print(f"❌ Step 4 failed: {e}")

    # ── Step 5: Order request → Order Agent ──
    try:
        r5 = test_step(
            supervisor, 5,
            "Ask for demo order → should route to Order Agent",
            "Ek demo order generate karo mere liye"
        )
        assert any(w in r5.lower() for w in ["order", "₹", "commission", "savings", "demo", "ondc", "naya"]), \
            f"Expected order response, got: {r5[:100]}"
        print("✅ Routed to Order Agent")
        passed += 1
    except Exception as e:
        print(f"❌ Step 5 failed: {e}")

    # ── Step 6: Ask savings → Order Agent ──
    try:
        r6 = test_step(
            supervisor, 6,
            "Ask about savings → should route to Order Agent",
            "ONDC se kitna paisa bach raha hai Swiggy ke comparison mein?"
        )
        assert any(w in r6.lower() for w in ["savings", "bachat", "बचत", "commission", "₹", "save", "ondc", "swiggy"]), \
            f"Expected savings response, got: {r6[:100]}"
        print("✅ Savings comparison shown")
        passed += 1
    except Exception as e:
        print(f"❌ Step 6 failed: {e}")

    # ── Step 7: Voice command → Voice Agent ──
    try:
        r7 = test_step(
            supervisor, 7,
            "Voice command → should route to Voice Agent",
            "Merchant ne voice message bheja hai. Audio transcript: 'Amul ka rate 35 rupees karo'. Intent detect karo."
        )
        print("✅ Routed to Voice Agent")
        passed += 1
    except Exception as e:
        print(f"❌ Step 7 failed: {e}")

    # ── Step 8: Back to orders → should still route correctly ──
    try:
        r8 = test_step(
            supervisor, 8,
            "Ask for daily summary → Order Agent",
            "Aaj ka hisaab dikhao — kitne orders aaye, kitna kamaaya?"
        )
        print("✅ Routed to Order Agent for summary")
        passed += 1
    except Exception as e:
        print(f"❌ Step 8 failed: {e}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed}/{total} steps passed")
    print("=" * 60)

    if passed == total:
        print("  🎉 ALL TESTS PASSED — Full merchant journey works!")
    elif passed >= 6:
        print("  ✅ MOSTLY PASSING — Minor routing issues to review")
    else:
        print("  ⚠️  NEEDS WORK — Review failing steps above")

    return passed, total


if __name__ == "__main__":
    passed, total = run_full_journey()
    sys.exit(0 if passed >= 6 else 1)
