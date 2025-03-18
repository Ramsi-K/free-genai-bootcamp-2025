from comps import MicroService, ServiceType, ServiceRoleType
import chromadb


class VectorStorage:
    def __init__(self):
        self.service = MicroService(
            name="vector_storage",
            service_type=ServiceType.STORAGE,
            role_type=ServiceRoleType.STORAGE,
        )
        self.client = chromadb.PersistentClient(path="/shared/data/chroma")
        self.collection = self.client.get_or_create_collection(
            "korean_transcripts"
        )

    async def store_vectors(self, embeddings, text, metadata=None):
        """Store embeddings in ChromaDB"""
        self.collection.add(
            embeddings=[embeddings],
            documents=[text],
            metadatas=[metadata] if metadata else None,
        )


storage_service = VectorStorage()
