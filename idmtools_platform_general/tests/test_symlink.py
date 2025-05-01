import os
import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from idmtools.core.platform_factory import Platform


class TestFilePlatformWithSymlink(unittest.TestCase):

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.platform = Platform("File", job_directory=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_link_file(self):
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_file = "test.txt"
        source_file = Path(temp_source_path, target_file)
        link_file = Path(temp_dest_path, target_file)

        # Create a source file
        with open(source_file, 'w') as f:
            f.write('This is a test file.')

        # Act
        self.platform.link_file(source_file, link_file)
        self.assertTrue(os.path.islink(link_file))

        # Verify the content
        with open(link_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'This is a test file.')

    def test_link_dir(self):
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_dir = "DEST"
        target_file = "test.txt"
        # Create the target directory inside temp_source_path
        target_dir_path = Path(temp_source_path, target_dir)
        target_dir_path.mkdir(parents=True, exist_ok=True)

        # Create the dest directory inside temp_dest_path
        link_dir_path = Path(temp_dest_path, target_dir)
        link_dir_path.mkdir(parents=True, exist_ok=True)

        source_file = target_dir_path / target_file
        link_file = link_dir_path / target_file

        # Create a source file
        with open(source_file, 'w') as f:
            f.write('This is a test file.')

        # symlink the link directory to target directory
        self.platform.link_dir(target_dir_path, link_dir_path)
        self.assertTrue(os.path.islink(link_dir_path))

        # Verify the content in link_file
        with open(link_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'This is a test file.')

    def test_sym_link_file_false(self):
        platform = Platform("File", job_directory=self.temp_dir.name, sym_link=False)
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_file = "test.txt"
        source_file = Path(temp_source_path, target_file)
        link_file = Path(temp_dest_path, target_file)

        # Create a source file
        with open(source_file, 'w') as f:
            f.write('This is a test file.')

        platform.link_file(source_file, link_file)
        self.assertFalse(os.path.islink(link_file))

    def test_sym_link_dir_false(self):
        platform = Platform("File", job_directory=self.temp_dir.name, sym_link=False)
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_dir = "DEST"
        target_file = "test.txt"
        # Create the target directory inside temp_source_path
        target_dir_path = Path(temp_source_path, target_dir)
        target_dir_path.mkdir(parents=True, exist_ok=True)

        # Create the dest directory inside temp_dest_path
        link_dir_path = Path(temp_dest_path, target_dir)
        link_dir_path.mkdir(parents=True, exist_ok=True)

        source_file = target_dir_path / target_file
        link_file = link_dir_path / target_file

        # Create a source file
        with open(source_file, 'w') as f:
            f.write('This is a test file.')

        # symlink the link directory to target directory
        platform.link_dir(target_dir_path, link_dir_path)
        self.assertFalse(os.path.islink(link_dir_path))

