import re

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    log_level: str = "info"

    question_prefix_regex: re.Pattern = re.compile("^\\s*!question\\s*")
    command_prefix_regex: re.Pattern = re.compile("^\\s*!(?P<command>\\S+)\\s*")

    @field_validator('command_prefix_regex', mode='after')
    @classmethod
    def validate_command_group(cls, v: re.Pattern) -> re.Pattern:
        # Check if the named group "command" exists
        if "command" not in v.groupindex:
            raise ValueError('Pattern must contain a named capture group (?P<command>...)')
        
        # Check that there is exactly 1 capture group in total
        if v.groups != 1:
            raise ValueError(f'Pattern must have exactly 1 capture group, but found {v.groups}')
            
        return v

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )

@lru_cache()
def get_settings():
    return Settings()