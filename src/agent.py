import logging
import datetime as dt
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents import function_tool, RunContext

# Import tool functions
from google_calendar_tool import add_event, get_upcoming_events
from google_mail_tool import send_email
from google_tasks_tool import (
    list_task_lists,
    list_tasks,
    create_task,
    update_task,
    delete_task,
)
from datetime_tool import get_current_datetime

# Import database functions
from database import save_credentials, get_credentials

logger = logging.getLogger("agent")

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a helpful voice AI assistant.
You are called Zephyr.
Speak in French by default
The user is interacting with you via voice,
even if you perceive the conversation as text.
You eagerly assist users with their questions by providing
information from your extensive knowledge.
Your responses are concise, to the point, and without
any complex formatting or punctuation including emojis,
asterisks, or other symbols.
You are curious, friendly, and have a sense of humor.
Do not hesitate to use the appropriate tool to determine the curren date.
""",
        )

# GOOGLE AUTH ##################################################################

    @function_tool
    async def update_google_creds(self, context: RunContext, creds_json: str):
        """
        Update the Google credentials for the user.
        This tool must be called before any other Google tool.
        """
        logger.info("Updating google credentials for user %s", context.participant.identity)
        save_credentials(context.participant.identity, creds_json)
        return "Google credentials updated."

# SAMPLE TOOL ##################################################################

    @function_tool
    async def lookup_weather(self, context: RunContext, location: str):
        """Use this tool to look up current weather information in the given location.

        If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.

        Args:
            location: The location to look up weather information for (e.g. city name)
        """

        logger.info(f"Looking up weather for {location}")

        return "sunny with a temperature of 70 degrees."

# DATE #########################################################################

    @function_tool
    async def get_current_datetime(self, context: RunContext):
        """Returns the current date and time in ISO format."""
        logger.info("Getting current date and time")
        return get_current_datetime()

# GOOGLE CALENDAR ##############################################################

    def _get_google_creds(self, context: RunContext) -> Credentials | None:
        creds_json = get_credentials(context.participant.identity)
        if not creds_json:
            return None
        return Credentials.from_authorized_user_info(json.loads(creds_json))

    @function_tool
    async def schedule_google_calendar_event(
        self,
        context: RunContext,
        summary: str,
        description: str,
        start_time: dt.datetime,
        end_time: dt.datetime,
        timezone: str = 'Europe/Paris'
    ):
        """Use this tool to schedule an event in Google Calendar.

        Args:
            summary: The summary or title of the event.
            description: The description of the event.
            start_time: The start time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
            end_time: The end time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
            timezone: The timezone for the event (default is 'Europe/Paris').
        """
        logger.info(f"Scheduling Google Calendar event: {summary} from {start_time} to {end_time}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return add_event(creds, summary, description, start_time, end_time)

    @function_tool
    async def get_next_scheduled_google_calendar_events(self, context: RunContext, count: int = 2):
        """Use this tool to retrieve next events in Google Calendar.

        Args:
            count: The number of upcoming events to retrieve (default is 2).
        """
        logger.info(f"Listing next Google Calendar events")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return get_upcoming_events(creds, count)

# GOOGLE MAIL ##################################################################

    @function_tool
    async def send_google_mail(self, context: RunContext, to: str, subject: str, message: str):
        """Use this tool to send an email using Gmail.

        Args:
            to: The recipient of the email.
            subject: The subject of the email.
            message: The content of the email.
        """
        logger.info(f"Sending email to {to} with subject {subject}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return send_email(creds, to, subject, message)

# GOOGLE TASKS #################################################################

    @function_tool
    async def list_google_task_lists(self, context: RunContext):
        """Use this tool to list the user's Google Task lists."""
        logger.info("Listing Google Task lists")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return list_task_lists(creds)

    @function_tool
    async def list_google_tasks(self, context: RunContext, task_list_id: str):
        """Use this tool to list the tasks in a specific Google Task list."""
        logger.info(f"Listing tasks for task list {task_list_id}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return list_tasks(creds, task_list_id)

    @function_tool
    async def create_google_task(
        self, context: RunContext, task_list_id: str, title: str, notes: str = None
    ):
        """Use this tool to create a new task in a specific Google Task list."""
        logger.info(f"Creating task '{title}' in task list {task_list_id}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return create_task(creds, task_list_id, title, notes)

    @function_tool
    async def update_google_task(
        self, context: RunContext, task_list_id: str, task_id: str, title: str, notes: str = None
    ):
        """Use this tool to update a task in a specific Google Task list."""
        logger.info(f"Updating task {task_id} in task list {task_list_id}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return update_task(creds, task_list_id, task_id, title, notes)

    @function_tool
    async def delete_google_task(self, context: RunContext, task_list_id: str, task_id: str):
        """Use this tool to delete a task in a specific Google Task list."""
        logger.info(f"Deleting task {task_id} from task list {task_list_id}")
        creds = self._get_google_creds(context)
        if not creds:
            return "Please authenticate with Google first."
        return delete_task(creds, task_list_id, task_id)

#

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

#

async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        # stt="assemblyai/universal-streaming:en",
        # stt="cartesia/ink-whisper:fr",
        stt="deepgram/nova-3:fr",
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm="openai/gpt-4.1-mini",
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts="cartesia/sonic-2:a167e0f3-df7e-4d52-a9c3-f949145efdab",
        # cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))