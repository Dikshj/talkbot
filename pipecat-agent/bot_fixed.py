"""TalkBot implemented as a Pipecat SmallWebRTC pipeline."""

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker, ProcessorUnusablePolicy
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair, LLMUserAggregatorParams
from pipecat.runner.types import RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.workers.runner import WorkerRunner

from tools_fixed import order_status_tool

load_dotenv()

SYSTEM_PROMPT = """You are TalkBot, a friendly and concise AI voice assistant.
Answer questions clearly using natural conversational language. Keep responses
short because they will be spoken aloud. Avoid unnecessary formatting. Ask
clarifying questions when required.

Use order_status_tool to check ORD101, ORD102, or ORD103. Never invent a status.
"""


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:
    stt = DeepgramSTTService(api_key=os.environ["DEEPGRAM_API_KEY"])
    tts = CartesiaTTSService(api_key=os.environ["CARTESIA_API_KEY"])
    llm = OpenAILLMService(api_key=os.environ["OPENAI_API_KEY"], settings=OpenAILLMService.Settings(system_instruction=SYSTEM_PROMPT))
    context = LLMContext(tools=[order_status_tool])
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context, user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()))
    pipeline = Pipeline([transport.input(), stt, user_aggregator, llm, tts, transport.output(), assistant_aggregator])
    worker = PipelineWorker(pipeline, params=PipelineParams(enable_metrics=True, enable_usage_metrics=True), processor_unusable_policy=ProcessorUnusablePolicy.END)
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(_transport, _client) -> None:
        logger.info("Pipecat client connected")
        context.add_message({"role": "developer", "content": "Say hello briefly."})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport, _client) -> None:
        logger.info("Pipecat client disconnected")
        await runner.cancel()

    await runner.add_workers(worker)
    await runner.run()


async def bot(runner_args: RunnerArguments) -> None:
    if not isinstance(runner_args, SmallWebRTCRunnerArguments):
        raise RuntimeError("TalkBot Pipecat backend requires the WebRTC runner")
    transport = SmallWebRTCTransport(webrtc_connection=runner_args.webrtc_connection, params=TransportParams(audio_in_enabled=True, audio_out_enabled=True))
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main
    main()

