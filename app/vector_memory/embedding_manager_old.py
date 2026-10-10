from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingManager:


    def __init__(
        self,
        model_name="all-MiniLM-L6-v2",
        batch_size=64
    ):

        print(
            f"[EMBEDDING] Loading model: {model_name}"
        )

        self.model_name = model_name

        self.batch_size = batch_size

        self.model = SentenceTransformer(
            model_name
        )

        print(
            "[EMBEDDING] Model loaded successfully."
        )



    # =====================================================
    # SINGLE TEXT EMBEDDING
    # =====================================================

    def encode(
        self,
        text
    ):

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding




    # =====================================================
    # MULTIPLE TEXT EMBEDDINGS
    # =====================================================

    def encode_batch(
        self,
        texts
    ):

        if not texts:
            return np.array([])


        print(
            f"[EMBEDDING] Encoding {len(texts)} texts"
        )


        all_embeddings = []


        # split into small batches
        for i in range(
            0,
            len(texts),
            self.batch_size
        ):

            batch = texts[
                i:i+self.batch_size
            ]


            embeddings = self.model.encode(
                batch,
                batch_size=self.batch_size,
                normalize_embeddings=True,
                show_progress_bar=False
            )


            all_embeddings.append(
                embeddings
            )


        final_embeddings = np.vstack(
            all_embeddings
        )


        print(
            f"[EMBEDDING] Generated embeddings: {final_embeddings.shape}"
        )


        return final_embeddings




    # =====================================================
    # EVENT MEMORY EMBEDDING
    # =====================================================

    def generate_embeddings(
        self,
        memories
    ):


        texts = []


        for memory in memories:

            description = memory.get(
                "description",
                ""
            )


            if description:

                texts.append(
                    description
                )


        if not texts:

            return np.array([])


        embeddings = self.encode_batch(
            texts
        )


        return embeddings