"""AgentCore Runtime entry point for Vyapari.ai supervisor agent.

Root-level entrypoint required by AgentCore direct_code_deploy.
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agents.supervisor import create_supervisor_agent

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """Main entry point invoked by AgentCore Runtime.

    Args:
        payload: Dict with 'prompt' (required), 'session_id' (optional)

    Returns:
        Dict with 'response' text and metadata
    """
    prompt = payload.get("prompt", "Namaste!")
    session_id = payload.get("session_id", "default")

    agent = create_supervisor_agent()
    result = agent(prompt)

    return {
        "response": result.message,
        "session_id": session_id,
        "agent": "supervisor",
    }


if __name__ == "__main__":
    app.run()
