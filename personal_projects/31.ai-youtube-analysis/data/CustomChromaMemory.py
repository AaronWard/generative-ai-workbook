from controlflow.memory.providers.chroma import ChromaMemory as BaseChromaMemory

class CustomChromaMemory(BaseChromaMemory):
    def __init__(self, client, collection_name="{key}", embedding_function=None):
        super().__init__(client=client, collection_name=collection_name)
        self._embedding_function = embedding_function  # Store embedding function internally

    def get_collection(self, memory_key: str):
        """
        Overrides the method to ensure embedding_function is passed to the collection.
        """
        name = self.collection_name.format(key=memory_key)
        if name not in [col.name for col in self.client.list_collections()]:
            collection = self.client.create_collection(
                name=name,
                embedding_function=self._embedding_function
            )
        else:
            collection = self.client.get_collection(
                name=name,
                embedding_function=self._embedding_function
            )
        return collection
