import os
from dotenv import load_dotenv
import openai
import pandas as pd
import requests

load_dotenv()
openai.organization = os.environ['OPENAI_ORG']
openai.api_key = os.environ['OPENAI_API_KEY']
API_URL = os.environ['API_URL']
headers = {"Authorization": "Bearer "+os.environ['TAPAS_API_KEY']}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def query_payload_name(df, name):
    df=df.astype(str)
    inputs = {
	"inputs": {
		"query": f"What is the Player of {name}?",
		"table": df.to_dict(orient='list')
	},
    }
    return inputs

def query_payload_posdfkm(df, name):
    df=df.astype(str)
    inputs = {
	"inputs": {
		"query": f"What is the Pos. DFKM of {name}?",
		"table": df.to_dict(orient='list')
	},
    }
    return inputs

def query_payload_age(df, name):
    df=df.astype(str)
    inputs = {
	"inputs": {
		"query": f"What is the age of {name}?",
		"table": df.to_dict(orient='list')
	},
    }
    return inputs

def query_payload_country(df, name):
    df=df.astype(str)
    inputs = {
	"inputs": {
		"query": f"What is the country of {name}?",
		"table": df.to_dict(orient='list')
	},
    }
    return inputs

def get_gpt3_completion(prompt, engine="davinci", **kwargs):
    engines = {
        'davinci': 'text-davinci-002',
        'curie': 'text-curie-001',
        'babbage': 'text-babbage-001',
        'ada': 'text-ada-001'
    }
    
    engine = engines.get(engine, engine)
    
    default = dict(
        max_tokens=3500 if engine == 'text-davinci-002' else 1500,
        stop=" END" if engine not in engines else None
    )
    
    final_kwargs = {**default, **kwargs}
    response = openai.Completion.create(
        prompt=prompt,
        engine=engine,
        **final_kwargs
    )
    
    answer = response['choices'][0]['text']
    return answer