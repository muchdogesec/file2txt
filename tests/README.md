# tests

## Test valid inputs

From the root of this code;

```shell
python3 -m unittest tests/test_1_output_file_generation.py
```

This script generates output files using a combination of file2txt settings.

You need to check the output manually to ensure it matches expectations.

## Test invalid inputs

```shell
python3 -m unittest tests/test_2_negative_tests.py
```

This will test invalid file input settings. All tests are expected to fail.