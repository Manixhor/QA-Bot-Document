import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from langchain_core.documents import Document
from rag_engine import RAGEngine
from storage import save_upload


class StorageTests(unittest.TestCase):
    def test_upload_validation_and_change_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ('../escape.txt', '/escape.txt', 'dir\\escape.txt', 'script.py'):
                with self.assertRaises(ValueError):
                    save_upload(directory, name, b'hello')
            with self.assertRaises(ValueError):
                save_upload(directory, 'empty.txt', b'')
            self.assertTrue(save_upload(directory, 'notes.txt', b'hello'))
            self.assertFalse(save_upload(directory, 'notes.txt', b'hello'))
            self.assertTrue(save_upload(directory, 'notes.txt', b'updated'))


class EngineTests(unittest.TestCase):
    def test_constructor_is_lazy(self):
        with patch('rag_engine.get_llm') as llm, patch('rag_engine.get_embeddings') as embeddings:
            RAGEngine()
            llm.assert_not_called()
            embeddings.assert_not_called()

    def test_upload_precedence_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            uploads, samples = root / 'uploads', root / 'samples'
            uploads.mkdir()
            samples.mkdir()
            (uploads / 'notes.txt').write_text('The uploaded document.')
            (samples / 'notes.txt').write_text('Outdated sample.')
            (uploads / 'broken.pdf').write_bytes(b'not a pdf')
            engine = RAGEngine()
            documents = engine.load_documents([uploads, samples])
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0].page_content, 'The uploaded document.')
            self.assertEqual(len(engine.load_errors), 1)

    def test_empty_library_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'blank.txt').write_text('   ')
            with self.assertRaises(FileNotFoundError):
                RAGEngine().load_documents([directory])

    def test_retrieve_validation_and_forwarding(self):
        engine = RAGEngine()
        engine.vector_store = Mock()
        for query in ('', ' ', None, 'x' * 4001):
            with self.assertRaises(ValueError):
                engine.retrieve(query)
        for k in (0, 11, True, 1.5):
            with self.assertRaises(ValueError):
                engine.retrieve('question', k)
        engine.retrieve(' question ', 4)
        engine.vector_store.similarity_search.assert_called_once_with('question', k=4)

    def test_answer_preserves_sources_and_includes_citations_in_context(self):
        llm = Mock()
        llm.invoke.return_value = SimpleNamespace(content='Python is a programming language [1].')
        engine = RAGEngine(llm=llm)
        engine.vector_store = Mock()
        document = Document(page_content='Python is a programming language.', metadata={'source': '/tmp/python.txt', 'page': 0})
        engine.vector_store.similarity_search.return_value = [document]
        result = engine.generate_answer('What is Python?')
        self.assertEqual(result['sources'][0]['content'], document.page_content)
        self.assertIn('[1] python.txt', llm.invoke.call_args.args[0][1][1])
        self.assertIn('[1]', result['answer'])

    def test_no_key_has_actionable_error(self):
        engine = RAGEngine()
        engine.vector_store = Mock()
        engine.vector_store.similarity_search.return_value = [Document(page_content='hello')]
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
            with self.assertRaisesRegex(ValueError, 'GROQ_API_KEY'):
                engine.generate_answer('hello')

    def test_no_results_does_not_call_provider(self):
        engine = RAGEngine(llm=Mock())
        engine.vector_store = Mock()
        engine.vector_store.similarity_search.return_value = []
        self.assertEqual(engine.generate_answer('unknown')['sources'], [])
        engine.llm.invoke.assert_not_called()
