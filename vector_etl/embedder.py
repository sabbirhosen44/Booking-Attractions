from sentence_transformers import SentenceTransformer

from vector_etl.config import VectorConfig


# Wraps the sentence-transformers model, loaded once
class Embedder:
    _model = None

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer(VectorConfig.EMBEDDING_MODEL)
        return cls._model

    @classmethod
    def encode_one(cls, text: str) -> list:
        return cls._get_model().encode(text).tolist()

    @classmethod
    def encode_batch(cls, texts: list) -> list:
        return cls._get_model().encode(texts).tolist()
