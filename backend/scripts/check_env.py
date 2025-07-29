import os
print(f"Working Directory: {os.getcwd()}")
print(f"__file__: {__file__}")
print(f"Absolute path: {os.path.abspath(__file__)}")

# List files in current directory
print("\nFiles in current directory:")
for item in os.listdir("."):
    print(f"  {item}")

# Check for test_batch_collection
test_path = "test_batch_collection"
print(f"\nChecking {test_path}:")
print(f"  Exists: {os.path.exists(test_path)}")
print(f"  Is directory: {os.path.isdir(test_path) if os.path.exists(test_path) else 'N/A'}")

# Check parent directory
parent_test_path = "../test_batch_collection"
print(f"\nChecking {parent_test_path}:")
print(f"  Exists: {os.path.exists(parent_test_path)}")
print(f"  Is directory: {os.path.isdir(parent_test_path) if os.path.exists(parent_test_path) else 'N/A'}")

# Try absolute path
abs_test_path = "/Users/bhunt/development/claude/personal/sp404mk2-sample-agent/test_batch_collection"
print(f"\nChecking {abs_test_path}:")
print(f"  Exists: {os.path.exists(abs_test_path)}")
print(f"  Is directory: {os.path.isdir(abs_test_path) if os.path.exists(abs_test_path) else 'N/A'}")