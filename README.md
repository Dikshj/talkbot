# TalkBot — real-time AI voice assistant

TalkBot is a small browser voice chatbot implemented twice: once with LiveKit Agents and once with Pipecat. Both implementations use the same provider chain (Deepgram streaming STT ? OpenAI LLM ? Cartesia streaming TTS), but the frameworks remain independent.

## Architecture

```text
React/Vite browser
  +- LiveKit mode: token API ? LiveKit room ? LiveKit AgentSession
  +- Pipecat mode: /pipecat/start ? SmallWebRTCTransport ? Pipecat Pipeline

Both: microphone ? VAD/turn detection ? streaming STT ? LLM context ? TTS ? speaker
```

LiveKit's `AgentSession` owns the media/session lifecycle, context, tool loop, and interruption behavior. Pipecat exposes the same flow as explicit processors. The frontend only selects the transport; it does not combine the frameworks in one pipeline.

## Requirements

- Python 3.11+
- Node.js 18+
- A LiveKit Cloud project for LiveKit mode
- Provider keys: `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`
- LiveKit mode additionally needs `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET`

Copy the relevant `.env.example` to `.env`. Secrets stay in backend folders and are never sent to the frontend.

## Run LiveKit mode

```powershell
cd livekit-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python agent.py dev
```

In a second terminal:

```powershell
cd livekit-agent
.\.venv\Scripts\Activate.ps1
uvicorn server:app --reload --port 8000
```

## Run Pipecat mode

```powershell
cd pipecat-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python bot.py -t webrtc
```

The Pipecat runner prints the local endpoint. Set `VITE_BACKEND_URL` in `frontend/.env` if it is not `http://localhost:7860`.

## Run the frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the displayed Vite URL, choose an implementation, and click **Start Conversation**. The app requests microphone permission, displays final transcript segments, and removes the audio element on disconnect.

## Tool calling

Ask: “Can you check order ORD102?” The model can call `get_order_status`, which returns:

- `ORD101`: Shipped
- `ORD102`: Out for delivery
- `ORD103`: Delivered

Unknown IDs return a not-found message; neither backend invents an order status. LiveKit registers the tool with `@function_tool`. Pipecat registers a `FunctionSchema` handler on `LLMContext`.

## Verification

```powershell
py -3.11 -m compileall -q livekit-agent pipecat-agent tests
py -3.11 -m pip install -r requirements-dev.txt
py -3.11 -m pytest -q tests
cd frontend
npm run build
```

The source checks do not prove provider connectivity. A real microphone test requires valid keys, a LiveKit project for LiveKit mode, browser microphone permission, and running the selected backend.

## Learning map

- **WebRTC:** carries microphone and speaker media with low latency.
- **Audio frames:** small chunks of PCM/audio data processed continuously instead of uploaded files.
- **STT:** turns streaming microphone audio into partial/final text.
- **VAD and turn detection:** identify speech and the end of a user turn.
- **LLM context:** stores the conversation history and tool calls for the current session.
- **TTS:** turns streamed model text into playable audio chunks.
- **Barge-in:** VAD detects new user speech and cancels the current bot response.
- **Time to first audio:** elapsed time from the end of the user turn until the first bot audio chunk; measure it by timestamping final STT and first TTS/audio events.

## LiveKit versus Pipecat

LiveKit is room-and-session oriented: the agent joins a WebRTC room and `AgentSession` hides much of the orchestration. Pipecat is pipeline oriented: each transport, processor, service, and aggregator is visible and ordered in Python. Both can support streaming, VAD, context, tool calls, and interruption handling; they differ mainly in where the orchestration abstraction lives.

Official references: [LiveKit Agents sessions](https://docs.livekit.io/agents/logic/sessions/), [LiveKit tools](https://docs.livekit.io/agents/logic/tools/), [Pipecat context and function calling](https://github.com/cartesia-ai/pipecat-docs/blob/main/pipecat/learn/context-management.mdx).
