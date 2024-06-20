import os
import shutil
import subprocess
import unittest
from tests.base_test import TEST_FILES_DIRECTORY, MODES, TEST_FILES, get_mimetype

def delete_directories():
    """Delete 'logs' and 'output/positive_tests' directories if they exist."""
    directories = ['logs', 'output/positive_tests']
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)

class TestFile2Txt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Delete directories once before running any tests."""
        delete_directories()

    def run_test(self, test_number, mode, file, defang, extract_text_from_image):
        input_filepath = os.path.join(TEST_FILES_DIRECTORY, file)
        # Get the MIME type of the input file
        mime_type = get_mimetype(file)

        # Create the output directory
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]
        output_directory = os.path.join('output', 'positive_tests', mode, filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        # Create a more descriptive output filename
        output_filename = f"{mode}_{filename_without_ext}_defang-{defang}_extract-{extract_text_from_image}_output.md"
        output_filepath = os.path.join(output_directory, output_filename)

        # Construct the command
        command = [
            "python3", "file2txt.py",
            "--mode", mode,
            "--file", input_filepath,
            "--output", output_filepath,
            "--defang", defang,
            "--extract_text_from_image", extract_text_from_image
        ]

        print(f"===TEST {test_number}=== Running command: {' '.join(command)}")
        print(f"MIME type of input file '{file}': {mime_type}")

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")

        self.assertEqual(result.returncode, 0, f"Command failed with error: {result.stderr}")

    def run_test_without_defang_extract(self, test_number, mode, file):
        input_filepath = os.path.join(TEST_FILES_DIRECTORY, file)
        # Get the MIME type of the input file
        mime_type = get_mimetype(file)

        # Create the output directory
        filename_without_ext = os.path.splitext(os.path.basename(file))[0]
        output_directory = os.path.join('output', 'positive_tests', mode, filename_without_ext)
        os.makedirs(output_directory, exist_ok=True)

        # Create a more descriptive output filename
        output_filename = f"{mode}_{filename_without_ext}_output.md"
        output_filepath = os.path.join(output_directory, output_filename)

        # Construct the command without --defang and --extract_text_from_image
        command = [
            "python3", "file2txt.py",
            "--mode", mode,
            "--file", input_filepath,
            "--output", output_filepath,
        ]

        print(f"===TEST {test_number} (No defang/extract)=== Running command: {' '.join(command)}")
        print(f"MIME type of input file '{file}': {mime_type}")

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")

        self.assertEqual(result.returncode, 0, f"Command failed with error: {result.stderr}")

    def test_all_modes(self):
        test_number = 1
        for mode, file_group in MODES.items():
            if file_group not in TEST_FILES:
                self.fail(f"No test files found for mode: {mode}")
                continue

            files = TEST_FILES[file_group]
            for file in files:
                for defang in ["false", "true"]:
                    for extract_text_from_image in ["false", "true"]:
                        if mode == "csv" and extract_text_from_image == "true":
                            continue  # Skip this combination for csv mode
                        print(f"===TEST {test_number}===")  # Print test number
                        with self.subTest(mode=mode, file=file, defang=defang, extract_text_from_image=extract_text_from_image):
                            self.run_test(test_number, mode, file, defang, extract_text_from_image)
                        test_number += 1  # Increment test number here, outside of subTest context

    def test_all_modes_without_defang_extract(self):
        test_number = 1
        for mode, file_group in MODES.items():
            if file_group not in TEST_FILES:
                self.fail(f"No test files found for mode: {mode}")
                continue

            files = TEST_FILES[file_group]
            for file in files:
                if mode == "csv":
                    continue  # Skip CSV mode for this set of tests
                print(f"===TEST {test_number}===")  # Print test number
                with self.subTest(mode=mode, file=file):
                    self.run_test_without_defang_extract(test_number, mode, file)
                test_number += 1  # Increment test number here, outside of subTest context

if __name__ == "__main__":
    unittest.main()
