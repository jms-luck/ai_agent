from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager


# Configuration for the LLM
# Note: Ensure that the API key and base URL are correctly set for your Azure OpenAI instance.
config_list = [
  {
        "model": "gpt-4o",
        "api_key": "your_api_key_here",  # Replace with your actual API key
        "base_url": "https://your_azure_openai_instance.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions",  # Replace with your actual base URL
        "api_version":  "2025-01-01-preview"
  }
]
llm_config = {
    "timeout": 600,
    "cache_seed": 42,  # Use 'cache_seed' instead of 'use_cache' (True becomes a seed value)
    "config_list": config_list,
}


# Define agents
planner = AssistantAgent(name="PlannerAgent", llm_config=llm_config)
infra_agent = AssistantAgent(name="InfraAgent", llm_config=llm_config)
reviewer = AssistantAgent(name="ReviewerAgent", llm_config=llm_config)

executor = AssistantAgent(
    name="CodeExecutor",
    llm_config=llm_config,
    code_execution_config={"work_dir": "deploy_project", "use_docker": False}
)

user_proxy = UserProxyAgent(
    name="User", 
    human_input_mode="NEVER",  # Set to NEVER to avoid human input or Set to ALWAYS for human input
    code_execution_config={"use_docker": False}  # Add this parameter to disable Docker
)

# Create group chat and manager
groupchat = GroupChat(
    agents=[user_proxy, planner, infra_agent, executor, reviewer],
    messages=["HELLO_MESSAGE"],
    max_round=5,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Start the deployment workflow
user_proxy.initiate_chat(
    manager,
    message="""
I want to deploy a static website hosted in the 'deploy_project' directory.
Please plan the steps, create necessary configuration files (like vercel.json or netlify.toml),
run deployment commands, and verify if the site is live.
""",
)
