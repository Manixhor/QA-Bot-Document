"""Exercise real Chroma persistence without API calls or embedding model downloads."""
import tempfile
import unittest
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from rag_engine import RAGEngine


class TopicEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        text = text.lower()
        return [float('python' in text), float('cloud' in text), 0.1]


class IndexTests(unittest.TestCase):
    def test_index_retrieval_reload_and_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            engine.create_vector_store([
                Document(page_content='Python is a programming language.', metadata={'source': 'python.txt'}),
                Document(page_content='Cloud computing rents remote servers.', metadata={'source': 'cloud.txt'}),
            ])
            self.assertEqual(engine.retrieve('Python', 1)[0].metadata['source'], 'python.txt')
            reloaded = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            reloaded.load_vector_store()
            self.assertEqual(reloaded.chunk_count, 2)
            self.assertEqual(reloaded.retrieve('Cloud', 1)[0].metadata['source'], 'cloud.txt')
            engine.create_vector_store([Document(page_content='Python updated.', metadata={'source': 'new.txt'})])
            self.assertEqual(engine.chunk_count, 1)
            self.assertEqual(engine.retrieve('Python', 1)[0].metadata['source'], 'new.txt')
            after = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            after.load_vector_store()
            self.assertEqual(after.chunk_count, 1)

    def test_failed_rebuild_keeps_previous_index(self):
        from langchain_chroma import Chroma
        with tempfile.TemporaryDirectory() as directory:
            engine = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            engine.create_vector_store([Document(page_content='Python original.')])
            with patch.object(Chroma, 'add_documents', side_effect=RuntimeError('embedding failed')):
                with self.assertRaises(RuntimeError):
                    engine.create_vector_store([Document(page_content='replacement')])
            self.assertEqual(engine.retrieve('Python', 1)[0].page_content, 'Python original.')
            reloaded = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            self.assertEqual(reloaded.retrieve('Python', 1)[0].page_content, 'Python original.')

    def test_browse_filters_document_without_query(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = RAGEngine(persist_directory=directory, embeddings=TopicEmbeddings())
            engine.create_vector_store([
                Document(page_content='Python passage.', metadata={'source': 'python.txt', 'page': 0}),
                Document(page_content='Cloud passage.', metadata={'source': 'cloud.txt'}),
            ])
            result = engine.browse('python.txt', limit=2)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['content'], 'Python passage.')
            self.assertEqual(result[0]['metadata']['page'], 0)
            self.assertEqual(engine.browse('missing.txt'), [])
            with self.assertRaises(ValueError):
                engine.browse('python.txt', limit=0)
