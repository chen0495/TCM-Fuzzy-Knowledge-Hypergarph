import json
import os
from typing import Dict, Any, List

def validate_llm_output(data: Any) -> bool:
    """Validates the basic structure of the LLM output dictionary.

    Args:
        data: The data returned and parsed from the LLM client.

    Returns:
        True if the basic structure ('entities' and 'relationships' keys with list values)
        is present, False otherwise.
    """
    if not isinstance(data, dict):
        print(f"Validation Error: Expected a dictionary, but got {type(data)}.")
        return False

    if 'entities' not in data:
        print("Validation Error: Missing 'entities' key in LLM output.")
        return False

    if 'relationships' not in data:
        print("Validation Error: Missing 'relationships' key in LLM output.")
        return False

    if not isinstance(data['entities'], list):
        print(f"Validation Error: 'entities' should be a list, but got {type(data['entities'])}.")
        return False

    if not isinstance(data['relationships'], list):
        print(f"Validation Error: 'relationships' should be a list, but got {type(data['relationships'])}.")
        return False

    # Optional: Add deeper validation here (e.g., check list items)
    print("LLM output structure validated successfully.")
    return True

def save_knowledge_json(data: Dict[str, Any], output_path: str):
    """Saves the extracted knowledge dictionary to a JSON file.

    Args:
        data: The dictionary containing extracted knowledge (assumed validated).
        output_path: The full path to the output JSON file.

    Raises:
        IOError: If there is an error writing the file.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir: # Check if dirname is not empty (for relative paths in root)
            os.makedirs(output_dir, exist_ok=True)

        print(f"Saving extracted knowledge to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Save successful.")

    except IOError as e:
        print(f"Error saving knowledge to JSON file {output_path}: {e}")
        raise # Re-raise the exception for the caller to handle if needed
    except Exception as e:
        # Catch other potential errors during file operations
        print(f"An unexpected error occurred during saving to {output_path}: {e}")
        raise

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("--- Running Output Parser Test ---")

    # --- Test Case 1: Valid Data ---
    print("\n--- Test Case 1: Valid Data ---")
    valid_data = {
        "entities": [{"entity_name": "A", "entity_type": "T1"}],
        "relationships": [{"relationship_type": "R1", "participants": []}]
    }
    print(f"Input Data: {valid_data}")
    is_valid = validate_llm_output(valid_data)
    print(f"Validation Result: {is_valid}")
    if is_valid:
        try:
            output_file_valid = os.path.join("output_test", "valid_output.json")
            save_knowledge_json(valid_data, output_file_valid)
            # Clean up the test file/dir if needed
            # if os.path.exists(output_file_valid): os.remove(output_file_valid)
            # if os.path.exists("output_test"): os.rmdir("output_test")
        except Exception as e:
            print(f"Error during save test for valid data: {e}")

    # --- Test Case 2: Invalid Data (Missing 'relationships') ---
    print("\n--- Test Case 2: Invalid Data (Missing 'relationships') ---")
    invalid_data_missing_key = {
        "entities": [{"entity_name": "B", "entity_type": "T2"}]
    }
    print(f"Input Data: {invalid_data_missing_key}")
    is_valid = validate_llm_output(invalid_data_missing_key)
    print(f"Validation Result: {is_valid}")

    # --- Test Case 3: Invalid Data (Not a dictionary) ---
    print("\n--- Test Case 3: Invalid Data (Not a dictionary) ---")
    invalid_data_wrong_type = ["list", "not", "dict"]
    print(f"Input Data: {invalid_data_wrong_type}")
    is_valid = validate_llm_output(invalid_data_wrong_type)
    print(f"Validation Result: {is_valid}")
    
    # --- Test Case 4: Invalid Data ('entities' is not a list) ---
    print("\n--- Test Case 4: Invalid Data ('entities' is not a list) ---")
    invalid_data_wrong_list_type = {
        "entities": {"entity_name": "C"}, # Should be a list
        "relationships": []
    }
    print(f"Input Data: {invalid_data_wrong_list_type}")
    is_valid = validate_llm_output(invalid_data_wrong_list_type)
    print(f"Validation Result: {is_valid}")

    print("\n--- Output Parser Test Finished ---") 