"""
Configuration loader utility for the data warehouse migration utility.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv
from loguru import logger


class ConfigLoader:
    """Load and manage configuration files."""

    def __init__(self, config_path: str = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = {}
        load_dotenv()  # Load environment variables from .env file

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from JSON or YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If file format is not supported
        """
        if config_path:
            self.config_path = config_path

        if not self.config_path:
            raise ValueError("No configuration file path specified")

        config_file = Path(self.config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        logger.info(f"Loading configuration from: {self.config_path}")

        # Load based on file extension
        if config_file.suffix.lower() in ['.json']:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        elif config_file.suffix.lower() in ['.yaml', '.yml']:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")

        # Replace environment variables in config
        self.config = self._replace_env_vars(self.config)

        logger.info("Configuration loaded successfully")
        return self.config

    def _replace_env_vars(self, config: Any) -> Any:
        """
        Recursively replace environment variable placeholders in configuration.

        Args:
            config: Configuration value (can be dict, list, or string)

        Returns:
            Configuration with environment variables replaced
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable value
            if config.startswith('${') and config.endswith('}'):
                env_var = config[2:-1]
                value = os.getenv(env_var)
                if value is None:
                    logger.warning(f"Environment variable not found: {env_var}")
                    return config
                return value
            return config
        else:
            return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'oracle.host')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_oracle_config(self) -> Dict[str, Any]:
        """Get Oracle database configuration."""
        return self.config.get('oracle', {})

    def get_snowflake_config(self) -> Dict[str, Any]:
        """Get Snowflake database configuration."""
        return self.config.get('snowflake', {})

    def get_informatica_config(self) -> Dict[str, Any]:
        """Get Informatica configuration."""
        return self.config.get('informatica', {})

    def get_mapping_config(self) -> Dict[str, Any]:
        """Get mapping configuration."""
        return self.config.get('mapping', {})

    def get_generation_config(self) -> Dict[str, Any]:
        """Get stored procedure generation configuration."""
        return self.config.get('generation', {})

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration."""
        return self.config.get('validation', {})

    def save_config(self, output_path: str) -> None:
        """
        Save current configuration to a file.

        Args:
            output_path: Path to save the configuration file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix.lower() in ['.json']:
            with open(output_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        elif output_file.suffix.lower() in ['.yaml', '.yml']:
            with open(output_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported output file format: {output_file.suffix}")

        logger.info(f"Configuration saved to: {output_path}")
