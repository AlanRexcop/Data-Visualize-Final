import os

def print_folder_structure(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            level = dirpath.replace(root_dir, '').count(os.sep)
            indent = '    ' * level
            f.write(f'{indent}{os.path.basename(dirpath)}/\n')
            subindent = '    ' * (level + 1)
            for filename in filenames:
                f.write(f'{subindent}{filename}\n')

if __name__ == "__main__":
    # Replace this with your desired directory
    directory_path = r"source"
    output_path = "tool/folder_structure.txt"
    
    print_folder_structure(directory_path, output_path)
    print(f"Folder structure written to '{output_path}'")
