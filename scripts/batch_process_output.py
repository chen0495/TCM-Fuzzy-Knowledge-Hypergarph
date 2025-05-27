#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from pathlib import Path
import sys

# Adjust the Python path to include the 'src' directory
# This allows importing modules from src (e.g., knowledge_extraction)
# Assumes the script is run from the project root or the 'scripts' directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from knowledge_extraction.extractor import KnowledgeExtractor
    from knowledge_extraction.output_parser import validate_llm_output, save_knowledge_json
except ImportError as e:
    print(f"Error importing modules. Make sure PYTHONPATH includes '{project_root / 'src'}' or run from project root.")
    print(f"Import Error: {e}")
    sys.exit(1)

# --- Constants ---
BASE_DIR = project_root
OUTPUT_DATA_DIR = BASE_DIR / "output_data"
RESULTS_DIR = OUTPUT_DATA_DIR / "extraction_results" # Save results within output_data
PROCESSED_LOG_FILE = BASE_DIR / "scripts" / "processed_output_files.log"

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper Functions ---

def load_processed_files(log_file: Path) -> set:
    """Loads the set of already processed file paths from the log file."""
    processed = set()
    if log_file.exists():
        try:
            with log_file.open('r', encoding='utf-8') as f:
                processed = {line.strip() for line in f if line.strip()}
            logging.info(f"Loaded {len(processed)} paths from {log_file}")
        except IOError as e:
            logging.error(f"Error reading processed log file {log_file}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error reading log file {log_file}: {e}")
    else:
        logging.info(f"Processed log file {log_file} not found. Starting fresh.")
    return processed

def process_single_file(file_path: Path, extractor: KnowledgeExtractor, processed_files_set: set, log_file: Path):
    """Processes a single text file for knowledge extraction."""
    abs_path_str = str(file_path.resolve())

    if abs_path_str in processed_files_set:
        logging.info(f"Skipping already processed file: {file_path.relative_to(BASE_DIR)}")
        return

    logging.info(f"Processing file: {file_path.relative_to(BASE_DIR)}")

    try:
        text = file_path.read_text(encoding='utf-8')
        if not text.strip():
            logging.warning(f"Skipping empty file: {file_path.relative_to(BASE_DIR)}")
            return
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return
    except UnicodeDecodeError as e:
        logging.error(f"Encoding error reading file {file_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return

    try:
        extracted_result = extractor.extract_knowledge(text)
    except Exception as e:
        logging.error(f"Extraction failed for {file_path.relative_to(BASE_DIR)}: {e}")
        return # Stop processing this file on extraction error

    if "error" in extracted_result:
        logging.error(f"LLM extraction error for {file_path.relative_to(BASE_DIR)}: {extracted_result['error']}")
        return # Stop processing this file if LLM reported an error

    if not validate_llm_output(extracted_result):
        logging.warning(f"Validation failed for extracted data from {file_path.relative_to(BASE_DIR)}. Skipping save.")
        # Optionally save the invalid output to a separate location for debugging
        # invalid_output_path = RESULTS_DIR / "invalid" / file_path.relative_to(OUTPUT_DATA_DIR).with_suffix(".json")
        # invalid_output_path.parent.mkdir(parents=True, exist_ok=True)
        # try:
        #     with invalid_output_path.open('w', encoding='utf-8') as f:
        #         json.dump(extracted_result, f, ensure_ascii=False, indent=2)
        # except Exception as e:
        #     logging.error(f"Could not save invalid output for {file_path.relative_to(BASE_DIR)}: {e}")
        return # Stop processing this file if validation fails

    # Construct output path, preserving subdirectory structure relative to OUTPUT_DATA_DIR
    relative_path = file_path.relative_to(OUTPUT_DATA_DIR)
    output_json_path = RESULTS_DIR / relative_path.with_suffix(".json")

    try:
        # Ensure the output directory exists
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        save_knowledge_json(extracted_result, str(output_json_path))
        logging.info(f"Successfully extracted and saved result to: {output_json_path.relative_to(BASE_DIR)}")
    except IOError as e:
        logging.error(f"Error saving JSON for {file_path.relative_to(BASE_DIR)} to {output_json_path}: {e}")
        return # Stop processing if saving fails
    except Exception as e:
        logging.error(f"Unexpected error saving JSON for {file_path.relative_to(BASE_DIR)}: {e}")
        return # Stop processing if saving fails

    # If saving was successful, log the processed file
    try:
        with log_file.open('a', encoding='utf-8') as f:
            f.write(abs_path_str + '\n')
        processed_files_set.add(abs_path_str)
        logging.debug(f"Added {abs_path_str} to processed log.") # Use debug level for less verbose logging
    except IOError as e:
        logging.error(f"Error appending to processed log file {log_file}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error writing to log file {log_file}: {e}")


# --- Main Execution ---

if __name__ == "__main__":
    logging.info("--- Starting Batch Knowledge Extraction Script ---")

    processed_files = load_processed_files(PROCESSED_LOG_FILE)

    try:
        logging.info("Initializing KnowledgeExtractor...")
        # Make sure any necessary environment variables for SiliconFlowClient are set
        knowledge_extractor = KnowledgeExtractor()
        logging.info("KnowledgeExtractor initialized successfully.")
    except Exception as e:
        logging.critical(f"Failed to initialize KnowledgeExtractor: {e}", exc_info=True)
        logging.info("--- Batch Knowledge Extraction Script Finished (Initialization Failed) ---")
        sys.exit(1) # Exit if extractor cannot be initialized

    logging.info(f"Scanning for .txt files in: {OUTPUT_DATA_DIR}")
    file_count = 0
    processed_count = 0
    error_count = 0 # Keep track of errors during processing loop

    # Ensure RESULTS_DIR exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for txt_file_path in OUTPUT_DATA_DIR.rglob('*.txt'):
        # Exclude files within the results directory itself if any .txt files end up there
        try:
            if RESULTS_DIR in txt_file_path.parents:
                continue
        except ValueError: # Handle cases where one path is not a subpath of the other
             pass


        file_count += 1
        try:
            process_single_file(txt_file_path, knowledge_extractor, processed_files, PROCESSED_LOG_FILE)
            # Simplistic check: if path not in processed_files before call AND now it is, count as processed
            # Note: This isn't perfect if process_single_file fails after adding to set but before finishing.
            # A more robust way might involve return values from process_single_file.
            if str(txt_file_path.resolve()) in processed_files:
                 # Check if it wasn't processed before the call (more accurate count)
                 # Requires storing the initial set size or comparing sets, simpler to just count files processed in the function
                 pass # Counting successful saves is handled by logging within the function now
        except Exception as e:
            logging.error(f"Unhandled exception processing file {txt_file_path}: {e}", exc_info=True)
            error_count += 1

    # Recalculate processed count based on final set size minus initial size
    final_processed_count = len(processed_files) - (len(load_processed_files(PROCESSED_LOG_FILE)) if PROCESSED_LOG_FILE.exists() else 0)


    logging.info(f"--- Batch Knowledge Extraction Script Finished ---")
    logging.info(f"Scanned {file_count} '.txt' files.")
    # This count reflects files successfully processed IN THIS RUN.
    # logging.info(f"Successfully processed and saved results for {processed_count} files in this run.")
    logging.info(f"Total files marked as processed (including previous runs): {len(processed_files)}")
    if error_count > 0:
        logging.warning(f"Encountered errors during processing for {error_count} files.") 