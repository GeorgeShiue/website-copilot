from dataclasses import dataclass

WEBPAGES_DATA_FOLDER_PATH = "data/webpages/prompt-v3"
DEFAULT_QDRANT_DB_FOLER_PATH = "data/rag/qdrant_db"


# TODO: 實作完整參數載入/驗證機制
@dataclass
class RagConfig:
    # ----- init args -----
    webpages_data_folder_path: str = WEBPAGES_DATA_FOLDER_PATH
    qdrant_db_folder_path: str = DEFAULT_QDRANT_DB_FOLER_PATH
    vector_store_collection_name: str = "webpages"
    force_rebuild: bool = False

    # ----- index args -----
    embedding_model_name: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 100
    paragraph_separator: str = "\n\n"

    # ----- query engine args -----
    llm_model_name: str = "gemini-3.1-flash-lite"
    similarity_top_k: int = 5
    similarity_cutoff: float = 0.5
