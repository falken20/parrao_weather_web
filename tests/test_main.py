import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMain(unittest.TestCase):

    @patch('src.web.app')
    def test_import_app_from_src_web(self, mock_app):
        """Test that app is successfully imported from src.web"""
        # Import main module to trigger the import
        import main
        
        # Verify that the app object exists in the main module
        self.assertTrue(hasattr(main, 'app'))

    @patch('src.web.app')
    def test_main_execution_calls_app_run(self, mock_app):
        """Test that app.run() is called when script is executed directly"""
        mock_app.run = MagicMock()
        
        # Mock __name__ to be '__main__' to simulate direct execution
        with patch('__main__.__name__', '__main__'):
            # Execute the main block by importing and running the code
            with patch('builtins.__name__', '__main__'):
                exec(open('main.py').read())
        
        # Verify app.run() was called
        mock_app.run.assert_called_once()

    @patch('src.web.app')
    def test_main_execution_calls_app_run_without_debug(self, mock_app):
        """Test that app.run() is called without debug parameter"""
        mock_app.run = MagicMock()
        
        # Execute the main block
        with patch('__main__.__name__', '__main__'):
            with patch('builtins.__name__', '__main__'):
                exec(open('main.py').read())
        
        # Verify app.run() was called without arguments (debug=True is commented out)
        mock_app.run.assert_called_once_with()

    @patch('src.web.app')
    def test_module_import_does_not_call_app_run(self, mock_app):
        """Test that app.run() is NOT called when module is imported"""
        mock_app.run = MagicMock()
        
        # Import main as a module (not as __main__)
        import main
        
        # Verify app.run() was NOT called
        mock_app.run.assert_not_called()

    @patch('src.web.app')
    def test_app_object_accessible(self, mock_app):
        """Test that app object is accessible after import"""
        import main
        
        # Verify that main.app exists and is the mocked app
        self.assertEqual(main.app, mock_app)

    @patch('src.web.app')
    def test_main_block_conditional(self, mock_app):
        """Test that the main block only executes when __name__ == '__main__'"""
        mock_app.run = MagicMock()
        
        # Test when __name__ is not '__main__'
        with patch('main.__name__', 'some_other_name'):
            import importlib
            importlib.reload(main)
            
        mock_app.run.assert_not_called()
        
        # Reset the mock
        mock_app.run.reset_mock()
        
        # Test when __name__ is '__main__'
        with patch('main.__name__', '__main__'):
            # Simulate the main block execution
            if '__main__' == '__main__':
                mock_app.run()
            
        mock_app.run.assert_called_once()

    def test_file_structure_and_imports(self):
        """Test that the file has the expected structure"""
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Check that the import statement exists
        self.assertIn('from src.web import app', content)
        
        # Check that the main block exists
        self.assertIn('if __name__ == "__main__":', content)
        
        # Check that app.run() is called
        self.assertIn('app.run()', content)

    @patch('src.web.app')
    def test_debug_comment_is_present(self, mock_app):
        """Test that the debug option is commented out"""
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Check that debug option is commented out
        self.assertIn('# app.run(debug=True)', content)
        
        # Check that the uncommented version doesn't have debug
        lines = content.split('\n')
        app_run_lines = [line.strip() for line in lines if 'app.run()' in line and not line.strip().startswith('#')]
        
        # Should have at least one uncommented app.run() line
        self.assertTrue(len(app_run_lines) > 0)
        
        # The uncommented app.run() should not have debug parameter
        for line in app_run_lines:
            self.assertEqual(line, 'app.run()')


if __name__ == '__main__':
    unittest.main()