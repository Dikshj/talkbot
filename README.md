# TalkBot — LiveKit real-time AI voice assistant

TalkBot is a minimal browser voice chatbot built with React, LiveKit Agents, Deepgram, OpenAI, and Cartesia.

```text
Browser microphone
      ?
LiveKit WebRTC room
      ?
Python LiveKit AgentSession
      ?
Deepgram STT ? OpenAI LLM ? Cartesia TTS
      ?
LiveKit audio track
      ?
Browser speaker
```

## Project structure

```text
talkbot/
+-- frontend/              React + TypeScript + Vite UI
+-- livekit-agent/         Python LiveKit Agents worker and token API
+-- tests/                 Deterministic tool tests
+-- README.md
```

## Required accounts and keys

- LiveKit Cloud project
- OpenAI API key
- Deepgram API key
- Cartesia API key

Copy `livekit-agent/.env.example` to `livekit-agent/.env` and fill in the values. Copy `frontend/.env.example` to `frontend/.env` if your URLs differ from the defaults. Never put provider secrets in the frontend.

## Run the LiveKit agent

Terminal 1 — agent worker:

```powershell
cd livekit-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python agent.py dev
```

Terminal 2 — token API:

```powershell
cd livekit-agent
.\.venv\Scripts\Activate.ps1
uvicorn server:app --reload --port 8000
```

Terminal 3 — frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, click **Start Conversation**, allow microphone access, and speak naturally. The frontend connects to the LiveKit room using a short-lived token from the FastAPI endpoint.

## How the flow works

1. React calls `POST /livekit/token`.
2. FastAPI creates a short-lived LiveKit room token.
3. React joins the LiveKit WebRTC room and publishes the microphone.
4. The Python agent joins the same room through `AgentServer`.
5. `AgentSession` sends audio to Deepgram for streaming transcription.
6. OpenAI generates a response using conversation context.
7. The model can call `get_order_status(order_id)` for mock orders.
8. Cartesia converts the response into streaming audio.
9. The agent publishes the audio back through LiveKit.
10. React attaches the incoming audio track to the browser speaker.

Silero VAD and LiveKit turn handling support natural turn-taking and barge-in. When the user speaks while TalkBot is speaking, the current response can be interrupted and the session listens to the new turn.

## Tool calling

Ask: “Can you check order ORD102?” The agent can call `get_order_status` from `livekit-agent/tools.py`.

- `ORD101`: Shipped
- `ORD102`: Out for delivery
- `ORD103`: Delivered

Unknown order IDs return a not-found message; the agent does not invent statuses.

## Verification

```powershell
cd C:\Users\diks2\talkbot
py -3.11 -m compileall -q livekit-agent tests
py -3.11 -m pip install -r requirements-dev.txt
py -3.11 -m pytest -q tests
cd frontend
npm run build
```

Static checks do not prove provider connectivity. A real voice test requires valid credentials, a LiveKit project, and browser microphone permission.

## Concepts

- **WebRTC:** low-latency microphone and speaker media transport.
- **STT:** converts streaming speech into text.
- **LLM:** generates the conversational response and decides when to call tools.
- **TTS:** converts text into streaming speech.
- **VAD:** detects when the user starts and stops speaking.
- **Barge-in:** interrupts an in-progress assistant response when the user speaks.
- **Time to first audio:** time from the end of the user turn until the first assistant audio chunk.
