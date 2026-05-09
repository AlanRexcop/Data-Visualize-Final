import os

def get_folder_structure(root_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '.gemini', '__pycache__', '.venv', 'venv', 'output', 'data'}
    
    structure = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        level = os.path.relpath(dirpath, root_dir).count(os.sep)
        if level == 0 and os.path.basename(dirpath) == '':
            dirname = os.path.basename(os.path.abspath(dirpath))
        else:
            dirname = os.path.basename(dirpath)
            
        indent = '    ' * level
        structure.append(f'{indent}{dirname}/')
        
        subindent = '    ' * (level + 1)
        for filename in filenames:
            structure.append(f'{subindent}{filename}')
            
    return "\n".join(structure)

def bundle_project(root_dir, output_file, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '.gemini', '__pycache__', '.venv', 'venv', 'output', 'data'}
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 1. Write Header and Folder Structure
        outfile.write(f"{'#'*80}\n")
        outfile.write(f"PROJECT BUNDLE: {os.path.basename(os.path.abspath(root_dir))}\n")
        outfile.write(f"DATE: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}\n")
        outfile.write(f"{'#'*80}\n\n")
        
        outfile.write("### FOLDER STRUCTURE ###\n")
        outfile.write(get_folder_structure(root_dir, exclude_dirs))
        outfile.write("\n\n")
        
        # 2. Write File Contents
        outfile.write("### FILE CONTENTS ###\n")
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            
            for file in filenames:
                # Filter for .py and .md files
                if file.endswith(('.py', '.md')):
                    file_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    # Write a clear header for the LLM
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"FILE: {rel_path}\n")
                    outfile.write(f"{'='*80}\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            outfile.write("\n")
                    except Exception as e:
                        outfile.write(f"[Error reading file {rel_path}: {e}]\n")

    print(f"Project bundled successfully into: {output_file}")

if __name__ == "__main__":
    # Target the project root
    project_root = os.getcwd()
    output_path = os.path.join(project_root, "tool", "project_bundle.txt")
    
    bundle_project(project_root, output_path)
