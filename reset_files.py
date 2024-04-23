import shutil
import json

def main():
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)

        # Clear the contents of the base_dir directory
        shutil.rmtree(config['base_dir'])
    except FileNotFoundError:
        pass  # Directory doesn't exist, nothing to delete


if __name__ == "__main__":
    main()