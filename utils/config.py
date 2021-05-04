from dynaconf import Dynaconf


settings = Dynaconf(
    envvar_prefix="CIRB",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
)
