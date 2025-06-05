from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
import time

# Configuration for Gemini API
config_list = [
    {
        "model": "gemini-1.5-flash",  # Changed to flash model - uses less quota
        "api_key": "your_api_key_here",  # Replace with your actual API key
        "api_type": "google",
        "base_url": "https://generativelanguage.googleapis.com/v1beta"
    }
]

# Remove invalid parameters: retry_wait_time and max_retries
llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": config_list,
}

# Define a fallback handler for quota exceeded errors
def create_agents_with_fallback():
    try:
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
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "deploy_project", "use_docker": False}
        )
        
        return planner, infra_agent, reviewer, executor, user_proxy
        
    except Exception as e:
        print(f"Error creating agents: {e}")
        print("Quota may have been exceeded. Please try again later or use a different API key.")
        exit(1)

# Create agents with error handling
planner, infra_agent, reviewer, executor, user_proxy = create_agents_with_fallback()

# Create group chat and manager with reduced complexity
groupchat = GroupChat(
    agents=[user_proxy, planner, infra_agent, executor, reviewer],
    messages=[],
    max_round=6,
    speaker_selection_method="round_robin",  # Changed from "manual" to avoid validation errors
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config=llm_config,
    system_message="You are a deployment coordinator. Keep responses concise to minimize API usage."
)

# Start the deployment workflow with error handling
try:
    user_proxy.initiate_chat(
        manager,
        message="""
I want to deploy a static website hosted in the 'deploy_project' directory.
Please plan the steps, create necessary configuration files (like vercel.json or netlify.toml),
run deployment commands, and verify if the site is live.
""",
    )
except Exception as e:
    if "RESOURCE_EXHAUSTED" in str(e):
        print("API quota exceeded. Please try again later or use a different API key.")
        print("For more information: https://ai.google.dev/gemini-api/docs/rate-limits")
    else:
        print(f"Error during chat: {e}")