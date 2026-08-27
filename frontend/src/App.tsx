import { useEffect, useRef, useState } from "react";
import { Room, RoomEvent, Track } from "livekit-client";
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import { BACKEND_URL, LIVEKIT_URL } from "./services/config";

type Mode = "livekit" | "pipecat";
type Message = { role: "user" | "assistant"; text: string };

export default function App() {
  const [mode, setMode] = useState<Mode>("livekit");
  const [status, setStatus] = useState("Disconnected");
  const [phase, setPhase] = useState("Idle");
  const [messages, setMessages] = useState<Message[]>([]);
  const room = useRef<Room | null>(null);
  const pipecat = useRef<PipecatClient | null>(null);

  const addMessage = (role: Message["role"], text: string) => {
    if (!text.trim()) return;
    setMessages((current) => [...current, { role, text: text.trim() }]);
  };

  const endConversation = async () => {
    await room.current?.disconnect();
    await pipecat.current?.disconnect();
    room.current = null;
    pipecat.current = null;
    setStatus("Disconnected");
    setPhase("Idle");
  };

  useEffect(() => () => { void endConversation(); }, []);

  const startLiveKit = async () => {
    setStatus("Connecting"); setPhase("Connecting");
    const response = await fetch(`${BACKEND_URL}/livekit/token`, { method: "POST" });
    if (!response.ok) throw new Error("Could not create LiveKit token");
    const { token } = await response.json();
    const nextRoom = new Room();
    nextRoom.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        const audio = track.attach();
        audio.autoplay = true;
        audio.setAttribute("data-talkbot-audio", "true");
        document.body.appendChild(audio);
      }
    });
    nextRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach((element) => element.remove());
    });
    nextRoom.on(RoomEvent.TranscriptionReceived, (segments) => {
      for (const segment of segments) if (segment.final) addMessage("assistant", segment.text);
    });
    await nextRoom.connect(LIVEKIT_URL, token);
    await nextRoom.localParticipant.setMicrophoneEnabled(true);
    room.current = nextRoom;
    setStatus("Connected"); setPhase("Listening");
  };

  const startPipecat = async () => {
    setStatus("Connecting"); setPhase("Connecting");
    const client = new PipecatClient({
      transport: new SmallWebRTCTransport(), enableMic: true, enableCam: false,
      callbacks: {
        onConnected: () => { setStatus("Connected"); setPhase("Listening"); },
        onDisconnected: () => { setStatus("Disconnected"); setPhase("Idle"); },
        onUserStartedSpeaking: () => setPhase("Listening"),
        onUserStoppedSpeaking: () => setPhase("Thinking"),
        onBotStartedSpeaking: () => setPhase("Speaking"),
        onBotStoppedSpeaking: () => setPhase("Listening"),
        onUserTranscript: (data: { text: string; final: boolean }) => { if (data.final) addMessage("user", data.text); },
        onBotTranscript: (data: { text: string }) => addMessage("assistant", data.text),
      },
    });
    await client.startBotAndConnect({ endpoint: `${BACKEND_URL}/pipecat/start` });
    pipecat.current = client;
  };

  const startConversation = async () => {
    try { await endConversation(); if (mode === "livekit") await startLiveKit(); else await startPipecat(); }
    catch (error) { setStatus("Disconnected"); setPhase("Error"); alert(error instanceof Error ? error.message : "Connection failed"); }
  };

  return <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100">
    <section className="mx-auto flex min-h-[90vh] max-w-3xl flex-col rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-2xl sm:p-10">
      <header className="flex items-center justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">Realtime voice AI</p><h1 className="mt-2 text-4xl font-bold">TalkBot</h1></div><label className="text-sm text-slate-400">Backend<select className="ml-2 rounded-lg bg-slate-800 px-3 py-2 text-slate-100" value={mode} onChange={(e) => { void endConversation(); setMode(e.target.value as Mode); }}><option value="livekit">LiveKit Agent</option><option value="pipecat">Pipecat Agent</option></select></label></header>
      <div className="mt-8 flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm"><span><span className={`mr-2 inline-block h-2.5 w-2.5 rounded-full ${status === "Connected" ? "bg-emerald-400" : "bg-slate-600"}`} />{status}</span><span className="text-cyan-300">{phase}</span></div>
      <div className="my-6 flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-800 bg-slate-950/50 p-4">{messages.length === 0 ? <p className="py-16 text-center text-slate-500">Start a conversation and ask TalkBot anything.</p> : messages.map((message, index) => <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[85%] rounded-2xl px-4 py-3 ${message.role === "user" ? "bg-cyan-600 text-white" : "bg-slate-800 text-slate-200"}`}>{message.text}</div></div>)}</div>
      <div className="flex flex-col items-center gap-5"><div className={`grid h-28 w-28 place-items-center rounded-full border-4 ${phase === "Speaking" ? "animate-pulse border-cyan-400 bg-cyan-400/20" : "border-slate-700 bg-slate-800"}`}><span className="text-5xl">🎙️</span></div><div className="flex gap-3"><button className="rounded-xl bg-cyan-500 px-5 py-3 font-semibold text-slate-950 hover:bg-cyan-400" onClick={() => void startConversation()} disabled={status === "Connecting"}>Start Conversation</button><button className="rounded-xl border border-slate-700 px-5 py-3 font-semibold hover:bg-slate-800" onClick={() => void endConversation()}>End Conversation</button></div><p className="text-center text-xs text-slate-500">Interrupt TalkBot naturally while it speaks. Your browser will ask for microphone permission.</p></div>
    </section>
  </main>;
}


