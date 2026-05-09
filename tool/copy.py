import os
import shutil

def copy_and_flatten_to_txt(src_dir, dst_dir):
  os.makedirs(dst_dir, exist_ok=True)
  
  for root, _, files in os.walk(src_dir):
    for file in files:
      src_file_path = os.path.join(root, file)
      
      # Create a new filename with .txt extension
      name_without_ext = os.path.splitext(file)[0]
      new_filename = f"{name_without_ext}.txt"
      dst_file_path = os.path.join(dst_dir, new_filename)

      shutil.copy2(src_file_path, dst_file_path)
      print(f"Copied: {src_file_path} -> {dst_file_path}")

def copy_with_structure_to_txt(src_dir, dst_dir):
    for root, _, files in os.walk(src_dir):
        for file in files:
            src_file_path = os.path.join(root, file)
            
            # Create destination path preserving structure
            relative_path = os.path.relpath(root, src_dir)
            dst_subfolder = os.path.join(dst_dir, relative_path)
            os.makedirs(dst_subfolder, exist_ok=True)
            
            # Convert to .txt extension
            name_without_ext = os.path.splitext(file)[0]
            new_filename = f"{name_without_ext}.txt"
            dst_file_path = os.path.join(dst_subfolder, new_filename)

            shutil.copy2(src_file_path, dst_file_path)
            print(f"Structured Copy: {src_file_path} -> {dst_file_path}")

def concatenate_to_single_txt(src_dir, output_file):
    """
    Reads all files in src_dir and writes them into one single text file
    with clear headers for each original file path.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(src_dir):
            for file in files:
                # Optional: Filter for specific extensions (e.g., only .py files)
                if not file.endswith('.py'):
                    continue

                src_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_file_path, src_dir)

                # Write a clear header for the LLM to recognize the file
                outfile.write(f"\n{'='*50}\n")
                outfile.write(f"FILE: {relative_path}\n")
                outfile.write(f"{'='*50}\n\n")

                try:
                    with open(src_file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n") # Ensure space between files
                except Exception as e:
                    outfile.write(f"[Error reading file: {e}]\n")

    print(f"Successfully concatenated all files into: {output_file}")


source_folder = "source"      
flatten_dst = "tool/flat"
structured_dst = "tool/structured"
combined_output = "tool/combined_codebase.txt"


# copy_and_flatten_to_txt(source_folder, flatten_dst)
# copy_with_structure_to_txt(source_folder, structured_dst)
concatenate_to_single_txt(source_folder, combined_output)
