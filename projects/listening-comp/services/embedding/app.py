from comps import MicroService, ServiceType, ServiceRoleType
from transformers import AutoModel, AutoTokenizer


class EmbeddingService:
    def __init__(self):
        self.service = MicroService(
            name="embedding",
            service_type=ServiceType.EMBEDDING,
            role_type=ServiceRoleType.ENCODER,
        )
        self.model = AutoModel.from_pretrained("jhgan/ko-sroberta-multitask")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "jhgan/ko-sroberta-multitask"
        )

    async def create_embeddings(self, text):
        """Create embeddings for Korean text"""
        tokens = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        embeddings = self.model(**tokens).last_hidden_state.mean(dim=1)
        return embeddings.detach().numpy()


embedding_service = EmbeddingService()
