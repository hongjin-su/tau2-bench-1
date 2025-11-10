"""Green agent implementation - manages assessment and evaluation."""

import json
import time
import tomllib
from typing import Optional

import dotenv
import gymnasium as gym
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, Message, SendMessageSuccessResponse
from a2a.utils import get_text_parts, new_agent_text_message
from agentify_tau_bench.utils import a2a_send_message, parse_tags
from loguru import logger

from tau2.data_model.simulation import RewardInfo, SimulationRun
from tau2.environment.tool import Tool
from tau2.gym import TAU_BENCH_ENV_ID, register_gym_agent

dotenv.load_dotenv()

RESPOND_ACTION_NAME = "respond"

# Register the environments (only needed once)
register_gym_agent()


def load_agent_card_toml(agent_name):
    current_dir = __file__.rsplit("/", 1)[0]
    with open(f"{current_dir}/{agent_name}.toml", "rb") as f:
        return tomllib.load(f)


def tools_to_str(tools: list[Tool]) -> str:
    return json.dumps([tool.openai_schema for tool in tools], indent=2)


async def ask_agent_to_solve(
    white_agent_url: str,
    env: gym.Env,
) -> Optional[SimulationRun]:

    terminated = False
    context_id = None
    observation, info = env.reset()
    # Access available tools and policy from info

    # Here, instead of calling white agent like calling an LLM, we need to present
    #   the assessment scenario to the white agent as if it is a independent task
    # Specifically, here we provide the tool information for the agent to reply with
    task_description = f"""
{info["policy"]}
Here's a list of tools you can use (you can use at most one tool at a time):
{tools_to_str(info["tools"])}
Please response in the JSON format. Please wrap the JSON part with <json>...</json> tags.
The JSON should contain:
- "name": the tool call function name, or "{RESPOND_ACTION_NAME}" if you want to respond directly.
- "arguments": the arguments for the tool call, or {{"content": "your message here"}} if you want to respond directly.
You should only use one tool at a time!!
You cannot respond to user and use a tool at the same time!!

Examples of responses:
<json>
{json.dumps({
    "name": "find_user_id_by_name_zip",
    "arguments": {
        "first_name": "Yusuf",
        "last_name": "Rossi",
        "zip_code": "19122"
    }
}, indent=2)}
</json>

<json>
{json.dumps({
    "name": "{RESPOND_ACTION_NAME}",
    "arguments": {
        "content": "Hello, how can I help you today?"
    }
}, indent=2)}
</json>

Next, I'll provide you with the user message and tool call results.
User message: {json.dumps(observation, indent=2)}
    """
    next_green_message = task_description
    while not terminated:
        logger.info(
            f"@@@ Green agent: Sending message to white agent{'ctx_id=' + str(context_id) if context_id else ''}... -->\n{next_green_message}"
        )
        white_agent_response = await a2a_send_message(
            white_agent_url, next_green_message, context_id=context_id
        )
        res_root = white_agent_response.root
        assert isinstance(
            res_root, SendMessageSuccessResponse
        ), f"Expected SendMessageSuccessResponse, got {type(res_root)}"
        res_result = res_root.result
        assert isinstance(
            res_result, Message
        ), f"Expected Message, got {type(res_result)}"
        if context_id is None:
            context_id = res_result.context_id
        else:
            assert (
                context_id == res_result.context_id
            ), "Context ID should remain the same in a conversation"

        text_parts = get_text_parts(res_result.parts)
        assert (
            len(text_parts) == 1
        ), "Expecting exactly one text part from the white agent"
        white_text = text_parts[0]
        logger.info(f"@@@ White agent response:\n{white_text}")
        # parse the action out
        white_tags = parse_tags(white_text)
        logger.info(f"@@@ White agent tags: {white_tags}")
        action_json = white_tags["json"]
        action_dict = json.loads(action_json)
        is_tool_call = action_dict["name"] != RESPOND_ACTION_NAME
        if not is_tool_call:
            action = action_dict["arguments"]["content"]
        else:
            action = json.dumps(action_dict)

        observation, reward, terminated, truncated, info = env.step(action)
        logger.info(f"@@@ Green agent: Observation: {observation}")
        logger.info(f"@@@ Green agent: Reward: {reward}")
        next_green_message = observation

        # instead of maintain history, just prepare the next message with the latest observation
        if terminated:
            break
    if info["simulation_run"] is not None:
        simulation_run = SimulationRun.model_validate_json(info["simulation_run"])
    else:
        simulation_run = None
    if info["reward_info"] is not None:
        reward_info = RewardInfo.model_validate_json(info["reward_info"])
        simulation_run.reward_info = reward_info
    return simulation_run


class TauGreenAgentExecutor(AgentExecutor):
    def __init__(self):
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # parse the task
        logger.info("Green agent: Received a task, parsing...")
        user_input = context.get_user_input()
        tags = parse_tags(user_input)
        white_agent_url = tags["white_agent_url"]
        env_config_str = tags["env_config"]
        env_config = json.loads(env_config_str)

        # set up the environment
        logger.info("Green agent: Setting up the environment...")

        logger.info(
            f"Green agent: Setting up the environment with config: {env_config}"
        )
        env_config["all_messages_as_observation"] = False
        env = gym.make(TAU_BENCH_ENV_ID, **env_config)

        metrics = {}

        logger.info("Green agent: Starting evaluation...")
        timestamp_started = time.time()
        res = await ask_agent_to_solve(
            white_agent_url,
            env,
        )
        logger.info(f"Green agent: Evaluation result: {res.model_dump_json(indent=2)}")

        metrics["time_used"] = time.time() - timestamp_started
        result_bool = metrics["success"] = res.reward_info.reward == 1
        result_emoji = "✅" if result_bool else "❌"

        logger.info("Green agent: Evaluation complete.")
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"Finished. White agent success: {result_emoji}\nMetrics: {metrics}\n"
            )
        )  # alternative, impl as a task-generating agent

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


def start_green_agent(agent_name="tau_green_agent", host="localhost", port=9001):
    logger.info("Starting green agent...")
    agent_card_dict = load_agent_card_toml(agent_name)
    url = f"http://{host}:{port}"
    agent_card_dict["url"] = url  # complete all required card fields

    request_handler = DefaultRequestHandler(
        agent_executor=TauGreenAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )

    uvicorn.run(app.build(), host=host, port=port)
