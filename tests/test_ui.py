import os
from pathlib import Path
from langchain_core.documents import Document
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


class FakeEngine:
    def __init__(self, **kwargs):
        self.chunk_count = 0
        self.load_errors = []
        self.questions = []

    def ingest(self, paths):
        self.chunk_count = 12

    def browse(self, source, limit=3):
        return [{"content": "A preview without a question.", "metadata": {"source": source}}]

    def retrieve(self, question, k=3):
        self.questions.append((question, k))
        return [Document(page_content="Python is a programming language.", metadata={"source": "python.txt", "page": 0})]

    def generate_answer(self, question, k=3):
        self.questions.append((question, k))
        return {'answer': 'Python is a language [1].', 'sources': [
            {'content': 'Python is a programming language.', 'metadata': {'source': 'python.txt', 'page': 0}}]}


def button(app, label):
    return next(item for item in app.button if item.label == label)


class UITests(unittest.TestCase):
    def test_empty_state_and_example_question(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
            app = AppTest.from_file(APP).run()
            self.assertFalse(app.exception)
            self.assertTrue(button(app, 'Search documents ↗').disabled)
            button(app, 'What is Python?').click().run()
            self.assertEqual(app.text_area[0].value, 'What is Python?')
            self.assertEqual(app.session_state['history'], [])
            self.assertFalse(app.exception)

    def test_process_answer_rerun_history_and_clear(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-only'}), patch('rag_engine.RAGEngine', FakeEngine):
            app = AppTest.from_file(APP).run()
            button(app, 'Process documents').click().run()
            self.assertFalse(app.exception)
            self.assertFalse(button(app, 'Find my answer ↗').disabled)
            app.text_area[0].input('What is Python?').run()
            button(app, 'Find my answer ↗').click().run()
            self.assertEqual(len(app.session_state['history']), 1)
            self.assertTrue(any('Page 1' in e.label for e in app.expander))
            app.slider[0].set_value(4).run()
            self.assertEqual(len(app.session_state['history']), 1)
            self.assertTrue(any('Python is a language' in m.value for m in app.markdown))
            button(app, 'Clear conversation').click().run()
            self.assertEqual(app.session_state['history'], [])
            self.assertFalse(app.exception)

    def test_library_change_requires_processing(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-only'}), patch('rag_engine.RAGEngine', FakeEngine):
            app = AppTest.from_file(APP).run()
            button(app, 'Process documents').click().run()
            app.checkbox[0].uncheck().run()
            self.assertTrue(button(app, 'Find my answer ↗').disabled)
            self.assertTrue(button(app, 'Process documents').disabled)
            self.assertFalse(app.exception)

    def test_source_search_works_without_api_key(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}), patch('rag_engine.RAGEngine', FakeEngine):
            app = AppTest.from_file(APP).run()
            button(app, 'Process documents').click().run()
            self.assertFalse(button(app, 'Search documents ↗').disabled)
            app.text_area[0].input('What is Python?').run()
            button(app, 'Search documents ↗').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['history'][-1]['mode'], 'Source search')
            self.assertEqual(app.session_state['history'][-1]['sources'][0]['content'], 'Python is a programming language.')
            app.radio[0].set_value('AI answer').run()
            self.assertTrue(button(app, 'Find my answer ↗').disabled)
            self.assertEqual(len(app.session_state['history']), 1)

    def test_provider_failure_keeps_previous_answer(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-only'}), patch('rag_engine.RAGEngine', FakeEngine):
            app = AppTest.from_file(APP).run()
            button(app, 'Process documents').click().run()
            app.text_area[0].input('What is Python?').run()
            button(app, 'Find my answer ↗').click().run()
            with patch.object(FakeEngine, 'generate_answer', side_effect=RuntimeError('provider down')):
                button(app, 'Find my answer ↗').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.session_state['history']), 1)
            self.assertTrue(app.error)

    def test_processing_failure_does_not_mark_workspace_ready(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}), patch('rag_engine.RAGEngine', FakeEngine), patch.object(FakeEngine, 'ingest', side_effect=ValueError('No readable text.')):
            app = AppTest.from_file(APP).run()
            button(app, 'Process documents').click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.session_state['ingested'])
            self.assertTrue(button(app, 'Search documents ↗').disabled)
            self.assertTrue(app.error)

    def test_browse_documents_needs_no_question_or_key(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}), patch('rag_engine.RAGEngine', FakeEngine):
            app = AppTest.from_file(APP).run()
            self.assertTrue(any('QA Bot Analysis' in h.value for h in app.sidebar.markdown))
            button(app, 'Process documents').click().run()
            app.radio[0].set_value('Browse documents').run()
            self.assertEqual(len(app.text_area), 0)
            self.assertFalse(button(app, 'Preview document ↗').disabled)
            button(app, 'Preview document ↗').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['history'][-1]['mode'], 'Browse documents')
            self.assertEqual(app.session_state['history'][-1]['sources'][0]['content'], 'A preview without a question.')

    def test_custom_question_survives_browse_mode(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
            app = AppTest.from_file(APP).run()
            app.text_area[0].input('What are the applications of machine learning?').run()
            app.radio[0].set_value('Browse documents').run()
            app.radio[0].set_value('Source search').run()
            self.assertEqual(app.text_area[0].value, 'What are the applications of machine learning?')
            self.assertFalse(app.exception)
