import yaml


def load_config(file_path: str) -> dict:
    """
    Load configuration file and return the content as a dictionary.
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config
