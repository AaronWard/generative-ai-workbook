"""
This script is a manager object for interacting
with a Chroma Database

Written by: Aaron Ward - 17nd November 2023
"""
import shutil
import chromadb
from pathlib import Path
from autogen.retrieve_utils  import query_vector_db, create_vector_db_from_dir
from autogen.token_count_utils import count_token

class ChromaDBManager:
    def __init__(self, docs_path, db_path, collection_name, model):
        self.docs_path = Path(docs_path)
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self._model = model
        self.client = self.get_client()
        self.custom_token_count_function = count_token
        self._doc_idx = -1


    def setup(self, clear_history=False):
        if not self.db_path.exists():
            if not self.docs_path.exists():
                raise ValueError(f"The docs directory at {self.docs_path} does not exist.")
            if clear_history:
                shutil.rmtree(self.db_path)
                print(f"Removed existing directory: {self.db_path}")

            self.client = self.create_vector_db()
        else:
            self.client = self.get_client()
        print(f"Chroma DB client set up at {self.db_path}")

    def create_vector_db(self, max_tokens=3000, chunk_mode="multi_lines"):
        client = create_vector_db_from_dir(
            dir_path=str(self.docs_path),
            client=self.get_client(),
            collection_name=self.collection_name,
            max_tokens=max_tokens,
            chunk_mode=chunk_mode
        )
        print("Chroma DB created successfully.")
        return client

    def get_client(self):
        """Load or create from directory"""
        return chromadb.PersistentClient(path=str(self.db_path))

    def query_db(self, query_texts, n_results=5):
        return query_vector_db(
            query_texts=query_texts,
            n_results=n_results,
            client=self.client,
            collection_name=self.collection_name
        )
    
    def get_context(self, results):
        doc_contents = ""
        current_tokens = 0
        _doc_idx = self._doc_idx
        _tmp_retrieve_count = 0
        for idx, doc in enumerate(results["documents"][0]):
            if idx <= _doc_idx:
                continue
            if results["ids"][0][idx] in self._doc_ids:
                continue
            _doc_tokens = self.custom_token_count_function(doc, self._model)
            if _doc_tokens > self._context_max_tokens:
                func_print = f"Skip doc_id {results['ids'][0][idx]} as it is too long to fit in the context."
                # print(func_print)
                self._doc_idx = idx
                continue
            if current_tokens + _doc_tokens > self._context_max_tokens:
                break
            func_print = f"Adding doc_id {results['ids'][0][idx]} to context."
            # print(func_print)
            # print(func_print, "green"), flush=True)
            current_tokens += _doc_tokens
            doc_contents += doc + "\n"
            self._doc_idx = idx
            self._doc_ids.append(results["ids"][0][idx])
            self._doc_contents.append(doc)
            _tmp_retrieve_count += 1
            if _tmp_retrieve_count >= self.n_results:
                break
        return doc_contents
