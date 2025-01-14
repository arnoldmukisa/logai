import os
import json
import logging
import traceback
from dotenv import load_dotenv
from ai21 import AI21Client
from ai21.models import Penalty

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.debug("Environment variables loaded from .env file")

# Get AI21 API key from environment variable
ai21_api_key = os.getenv("AI21_API_KEY")
if ai21_api_key:
    logger.debug("AI21 API key loaded successfully")
else:
    logger.error("Failed to load AI21 API key. Make sure it's set in the .env file.")
    exit(1)

# Initialize AI21 client
client = AI21Client(api_key=ai21_api_key)

def analyze_with_ai21(prompt, text):
    logger.debug(f"Sending request to AI21 for prompt: {prompt[:50]}...")
    try:
        full_prompt = f"{prompt}\n\nLog file:\n{text}"
        response = client.completion.create(
            prompt=full_prompt,
            max_tokens=500,
            model="j2-ultra",
            temperature=0.7,
            top_p=1,
            top_k_return=0,
            stop_sequences=["##"],
            num_results=1,
            custom_model=None,
            count_penalty=Penalty(scale=0),
            frequency_penalty=Penalty(scale=0),
            presence_penalty=Penalty(scale=0),
        )
        logger.debug("Received response from AI21")
        return response.completions[0].data.text.strip()
    except Exception as e:
        logger.error(f"Error in AI21 API call: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def process_log_file(file_path, prompts):
    logger.info(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r') as file:
            log_content = file.read()
        
        results = []
        for prompt_dict in prompts:
            prompt = prompt_dict['prompt']
            result = analyze_with_ai21(prompt, log_content)
            results.append({"prompt": prompt, "result": result})
        
        return results
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Load prompts from JSON file
try:
    with open('prompts_v2.json', 'r') as f:
        prompts = json.load(f)
    logger.debug("Prompts loaded successfully from prompts.json")
except Exception as e:
    logger.error(f"Error loading prompts.json: {str(e)}")
    logger.error(traceback.format_exc())
    exit(1)

# Get all .log files from the 'logs' directory
logs_dir = 'sample_logs_v1'
try:
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
    logger.info(f"Found {len(log_files)} log files in {logs_dir} directory")
except Exception as e:
    logger.error(f"Error reading log files from {logs_dir}: {str(e)}")
    logger.error(traceback.format_exc())
    exit(1)

results = {}

for log_file in log_files:
    file_path = os.path.join(logs_dir, log_file)
    results[log_file] = process_log_file(file_path, prompts)

# Output results
print("\n=== Analysis Results ===\n")
for log_file, file_results in results.items():
    print(f"File: {log_file}")
    if file_results:
        for result in file_results:
            print(f"\nPrompt: {result['prompt']}")
            print(f"Result:\n{result['result']}")
            # add separator
            print("\n" + "-"*50 + "\n")
    else:
        print("  Failed to process this file")
    print("\n" + "="*50 + "\n")

logger.debug("Script execution completed")