import os
import time
import pandas as pd
import utilities as util
import logging
import json
import reset_files
from code_generator import CodeGenerator

def setup_logging(config):
    # Setup logging
    log_file = config['log_file']
    # Remove the log file if it already exists
    if os.path.exists(log_file):
        os.remove(log_file)
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    # Run reset_files.py
    reset_files.main()

    # setup config file
    with open('config.json') as config_file:
        config = json.load(config_file)

    # setup logging　＆Initialize Code Generator
    setup_logging(config)
    generator = CodeGenerator(config)

    # start generating code with log
    start_time = time.time()
    generator.generate()
    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f"Code generation completed in {execution_time} seconds.")
    print(f"Code generation completed in {execution_time} seconds.")


if __name__ == "__main__":
    main()


