from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix='COMMISHBOT',
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True
)
