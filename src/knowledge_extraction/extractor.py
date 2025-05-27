import json
from typing import Dict, Any
import os

# Assuming llm_client and prompts are in the same directory or PYTHONPATH is set
from .llm_client import SiliconFlowClient
from .prompts import format_prompt, EXAMPLE_CASE # Import EXAMPLE_CASE for testing
from .output_parser import validate_llm_output, save_knowledge_json

class KnowledgeExtractor:
    """Orchestrates the knowledge extraction process using an LLM client."""

    def __init__(self):
        """Initializes the KnowledgeExtractor with an LLM client."""
        try:
            self.llm_client = SiliconFlowClient()
            print("SiliconFlowClient initialized successfully.")
        except ValueError as e:
            print(f"Error initializing SiliconFlowClient: {e}")
            # Depending on requirements, might re-raise or handle differently
            raise
        except Exception as e:
            print(f"An unexpected error occurred during client initialization: {e}")
            raise

    def extract_knowledge(self, text: str) -> Dict[str, Any]:
        """Extracts entities and relationships from the given text.

        Args:
            text: The input text (e.g., a medical case report).

        Returns:
            A dictionary containing the extracted 'entities' and 'relationships',
            or an error dictionary if extraction fails.
        """
        if not isinstance(text, str) or not text.strip():
            print("Error: Input text cannot be empty.")
            return {"error": "Input text cannot be empty."}

        try:
            print("Formatting prompt...")
            formatted_prompt = format_prompt(text)
            # print(f"Formatted Prompt:\n{formatted_prompt[:500]}...") # Optional: Log part of the prompt
            
            print("Requesting completion from LLM...")
            # Ensure llm_client was initialized
            if not hasattr(self, 'llm_client'):
                 print("Error: LLM Client was not initialized.")
                 return {"error": "LLM Client not initialized."}
                 
            extracted_data = self.llm_client.get_completion(formatted_prompt)
            print("Completion received successfully.")
            
            # Basic validation of the returned structure (optional but recommended)
            if not isinstance(extracted_data, dict) or \
               'entities' not in extracted_data or \
               'relationships' not in extracted_data:
                print(f"Warning: LLM output structure might be invalid. Data: {extracted_data}")
                # Depending on strictness, could return an error or the data as is

            return extracted_data

        except Exception as e:
            # Catching exceptions from format_prompt or get_completion
            print(f"Error during knowledge extraction: {e}")
            return {"error": f"Extraction failed: {e}"}

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("--- Running Knowledge Extractor Test ---")
    extractor = None # Initialize extractor to None
    try:
        extractor = KnowledgeExtractor()
    except Exception as e:
        # Catch initialization errors
        print(f"Extractor Initialization Error: {e}")
        print("--- Knowledge Extractor Test Finished (Initialization Failed) ---")
        exit() # Exit if initialization fails

    print("\n--- Using Example Case Text ---")
    test_text = '''病名: 内伤发热（高热）

例三刘Xx，男，17岁，门诊号：565375。初诊日期：1965年10月21日。患者于了月中旬劳动后，淋浴感寒而致发热（39℃），一56一经西药治疗两周发热仍未退。住院期间，每日下午体温波动于38．℃上下。经西医多种检查未能明确诊断。发热运今已三月余。来诊时每天下午4点至夜间2点发热（38．5℃），烧前先有恶寒，继而身热，无汗，伴有头晕，咽干，胸部觉隐痛，随后汗出热退，饮食尚可，二便一般。舌苔自厚、质红。脉细稍数，略显浮象。辨证；阴虚发热，营卫不和。治法：养阴清热，调和营卫。方药：青蒿10克鳖甲10克秦充6克地骨皮12克玄参12克银花15克天花粉15克鲜生地12克丹皮10克赤白芍各10克僵蚕6克鲜石斛30克灯芯1．5克桂枝3克甘草6克鲜茅根30克银柴胡3克10月25日：服上方4剂后，热势稍减，下午体温38．9℃，胸部时痛，脉滑稍数，上方去桂枝加常山3．5克，银柴胡改为3．5克，继服6剂。11月1日：药后曾有两天体温正常，昨日又达38℃苔白较厚，脉细数。患者日哺发热，属于阳明气机不畅，积热不清，上方加焦槟榔10克，蝉蜕3．5克，继服6剂。11月8日。烧未大作，昨日体温37．st，右侧耳痛，流黄水（素有中耳炎），别无不适，脉沉细稍数，舌苔白，上方再进4剂。皿月12日：近日发烧未作，一般清况良好。巛关幼波临床经验选》）［评按］内伤发热系指脏腑气血虚损或失调所引起的发热。白于阴阳气血偏虚而致者为虚热；因气滞、血瘀、食滞而致者为实热。本组病

例均为高热不退，连同下节“低热”，一57一均属内伤发热范畴。

例三发热已三月余，因其夜热早凉，咽干、舌红，脉细数，证属阴虚发热，故取青蒿鳖甲汤、清骨散加减，以清阴分伏热，又因时值深秋，且有恶寒发热汗出，故合桂枝汤以调和营卫。全方仍本解肌透邪、清营养阴除热而设，后加常山、焦榔、蝉蜕祛痰导滞，宣达气机，内外调和而愈。
'''

    # Define output path
    # Assuming you want to save output relative to the project root
    # Get the project root directory (assuming extractor.py is in src/knowledge_extraction)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_directory = os.path.join(project_root, "output_data", "extraction_results")
    output_file_path = os.path.join(output_directory, "example_case_extraction.json")

    print(f"Input Text:\n{test_text}...\n")
    print(f"Output will be saved to: {output_file_path}")

    extracted_result = extractor.extract_knowledge(test_text)

    print("\n--- Extraction Result ---")
    if "error" in extracted_result:
        print(f"Extraction failed: {extracted_result['error']}")
    else:
        # Print raw result before validation
        print("Raw Extracted Data:")
        print(json.dumps(extracted_result, indent=2, ensure_ascii=False))

        print("\n--- Validating Output Structure ---")
        is_valid = validate_llm_output(extracted_result)

        if is_valid:
            print("\n--- Saving Valid Output ---")
            try:
                save_knowledge_json(extracted_result, output_file_path)
            except Exception as e:
                print(f"Failed to save the output: {e}")
        else:
            print("\nValidation failed. Output will not be saved.")

    print("\n--- Knowledge Extractor Test Finished ---") 