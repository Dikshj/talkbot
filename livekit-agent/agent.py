"""TalkBot implemented with LiveKit Agents 1.x."""

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, function_tool
from livekit.plugins import cartesia, deepgram, openai, silero

from tools import get_order_status

load_dotenv()

INSTRUCTIONS = """You are TalkBot, a friendly and concise AI voice assistant.
Answer questions clearly using natural conversational language. Keep responses
short because they will be spoken aloud. Avoid unnecessary formatting. Ask
clarifying questions when required.

You can check mock order status with get_order_status. Never invent an order
status. If an order is not in the tool result, say that you could not find it.
"""


class TalkBot(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

    @function_tool
    async def get_order_status(self, order_id: str) -> str:
        """Look up a mock order status by ID; never invent a result."""
        return get_order_status(order_id)


server = AgentServer()


@server.rtc_session(agent_name="talkbot-livekit")
async def entrypoint(ctx: agents.JobContext) -> None:
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        max_tool_steps=3,
    )

    await session.start(
        room=ctx.room,
        agent=TalkBot(),
    )


if __name__ == "__main__":
    agents.cli.run_app(server)


