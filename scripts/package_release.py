# als subzero release packaging script
import os
import zipfile
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, 'ALS-SubZero-release.zip')
EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.archify', 'build', 'dist', '.idea', '.vscode', 'docs_external'}
EXCLUDED_FILES = {'VERIFICATION_AUTHENTICATION_GUIDE.txt', 'ALS-SubZero-release.zip'}
EXCLUDED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.o', '.zip', '.log'}
PRESERVED_DOTFILES = {'.gitignore', '.gitattributes', '.editorconfig', '.linkspector.yml'}

def build_release_zip():
    print(f'Creating release package: {OUTPUT_ZIP}...')
    if os.path.exists(OUTPUT_ZIP):
        try:
            os.remove(OUTPUT_ZIP)
        except OSError:
            pass
    file_count = 0
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                if file in EXCLUDED_FILES:
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDED_EXTENSIONS:
                    continue
                if file.startswith('.') and file not in PRESERVED_DOTFILES:
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, PROJECT_ROOT)
                if os.path.abspath(abs_path) == os.path.abspath(OUTPUT_ZIP):
                    continue
                norm_rel_path = rel_path.replace('\\', '/')
                if norm_rel_path.startswith('researchTemplate/'):
                    clean_rel_path = norm_rel_path.replace('researchTemplate/', 'paper/', 1)
                elif norm_rel_path == 'researchTemplate':
                    clean_rel_path = 'paper'
                else:
                    clean_rel_path = norm_rel_path
                archive_name = os.path.join('ALS-SubZero', clean_rel_path).replace('\\', '/')
                zf.write(abs_path, archive_name)
                file_count += 1
    size_kb = os.path.getsize(OUTPUT_ZIP) / 1024.0
    print(f'Successfully packaged {file_count} files into {OUTPUT_ZIP} ({size_kb:.1f} KB).')
    return OUTPUT_ZIP
if __name__ == '__main__':
    build_release_zip()