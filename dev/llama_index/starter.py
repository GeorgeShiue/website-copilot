import asyncio
import os

from llama_index.core.workflow import Context
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import StorageContext, load_index_from_storage

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_LLAMA_INDEX_TEST_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key



# Check if we have a persisted index, otherwise create one from the documents
if os.path.exists("storage"):
    storage_context = StorageContext.from_defaults(persist_dir="storage")
    index = load_index_from_storage(storage_context)
    print("Loaded index from storage.")
else:
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist("storage")
    print("Created new index and persisted to storage.")

query_engine = index.as_query_engine()

async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)

def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b

# Create an enhanced workflow with both tools
agent = FunctionAgent(
    tools=[multiply, search_documents],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt="""You are a helpful assistant that can perform calculations
    and search through documents to answer questions.""",
)

# Make agent remember the conversation context
ctx = Context(agent)

# Now we can ask questions about the documents or do calculations
async def main():
    response = await agent.run(
        "What did the author do in college? Also, what's 7 * 8?",
        ctx=ctx,
    )
    print(response)
    response = await agent.run(
        "What question did I just ask you?",
        ctx=ctx,
    )
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
