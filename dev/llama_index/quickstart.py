from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os

from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENAI_LLAMA_INDEX_TEST_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

documents = SimpleDirectoryReader("/home/george/website-copilot/data/test/webpage_enhanced_markdown").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
print(query_engine.query("介紹實驗室"))
