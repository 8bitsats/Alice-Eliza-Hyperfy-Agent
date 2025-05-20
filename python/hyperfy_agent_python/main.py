import os
import sys
import logging
import argparse
import json5
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import agent types
from src.agents.alice_agent import AliceAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hyperfy_agent.log')
    ]
)

logger = logging.getLogger("hyperfy")

def load_config(config_path=None):
    """
    Load configuration from a file or use defaults
    """
    # Default config path
    if not config_path:
        config_path = PROJECT_ROOT / "config.py"
        
    if config_path.endswith(".py"):
        # Load Python config module
        config_dir = os.path.dirname(config_path)
        config_name = os.path.basename(config_path).replace(".py", "")
        
        # Add to Python path
        sys.path.insert(0, config_dir)
        
        try:
            config_module = __import__(config_name)
            
            # Extract all uppercase variables as config
            config = {key: value for key, value in config_module.__dict__.items() 
                     if key.isupper()}
            
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    elif config_path.endswith(".json") or config_path.endswith(".json5"):
        # Load JSON config
        try:
            with open(config_path, 'r') as f:
                config = json5.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    else:
        logger.error(f"Unsupported config file format: {config_path}")
        return {}

def create_agent(agent_type, config):
    """
    Create an agent instance based on type
    """
    if agent_type.lower() == "alice":
        return AliceAgent(config)
    else:
        logger.error(f"Unknown agent type: {agent_type}")
        return None

def main():
    """
    Main entry point for Hyperfy Agent Starter Kit
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hyperfy Agent Python Starter Kit")
    parser.add_argument("--agent", "-a", type=str, default="alice", help="Agent type (e.g., alice)")
    parser.add_argument("--config", "-c", type=str, help="Path to config file")
    parser.add_argument("--log-level", "-l", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Load configuration
    config = load_config(args.config)
    
    # Update config with any environment variables
    for key, value in os.environ.items():
        if key.startswith("HYPERFY_"):
            config_key = key.replace("HYPERFY_", "")
            config[config_key] = value
    
    # Create agent
    agent = create_agent(args.agent, config)
    if not agent:
        logger.error(f"Failed to create agent of type {args.agent}")
        return 1
    
    # Start agent
    try:
        agent.start()
        
        # Keep the main thread running
        logger.info(f"{args.agent.title()} agent is running. Press Ctrl+C to exit.")
        while True:
            # The agent runs in its own thread, so we just need to keep the main thread alive
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        agent.stop()
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        agent.stop()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
