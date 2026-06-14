import yaml

def load_symbols(config_path: str = "config/symbols.yaml") -> list[str]:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config["symbols"]
