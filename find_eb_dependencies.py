#!/usr/bin/env python3

import re
import os

def parse_eb_file(file_path):
    """Parse an easyconfig file and extract dependencies."""
    
    dependencies = []
    build_dependencies = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Finding builddependencies block
        build_dep_match = re.search(r'builddependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if build_dep_match:
            build_deps_text = build_dep_match.group(1)
            # Extract dependencies using regex pattern that captures name and version
            build_deps = re.findall(r"\(\s*['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]", build_deps_text)
            build_dependencies = [f"{name}/{version}" for name, version in build_deps]
        
        # Finding dependencies block
        dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if dep_match:
            deps_text = dep_match.group(1)
            # Extract dependencies using regex pattern that captures name and version
            deps = re.findall(r"\(\s*['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]", deps_text)
            dependencies = [f"{name}/{version}" for name, version in deps]
            
        return build_dependencies + dependencies
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def extract_module_base(module_full_name):
    """Extract module name and version without toolchain.
    E.g., 'util-linux/2.39-GCCcore-12.3.0' becomes 'util-linux/2.39'
    """
    parts = module_full_name.split('/')
    if len(parts) != 2:
        return module_full_name  # Return original if it doesn't match expected format
    
    name = parts[0]
    version_parts = parts[1].split('-')
    
    # Either use the first part of version or join all parts up to the toolchain
    # For example, '2.39-GCCcore-12.3.0' -> '2.39'
    base_version = version_parts[0]
    
    # For special cases like SciPy-bundle/2023.07-gfbf-2023a, keep more of the version
    if 'gfbf' in parts[1] or 'foss' in parts[1] or 'intel' in parts[1]:
        # These are special stack identifiers, not toolchain versions
        base_version = '-'.join(version_parts[:2])
    
    return f"{name}/{base_version}"

def main():
    # Read the list of modules to search for
    with open('missed_modules.txt', 'r') as f:
        modules_to_find_full = [line.strip() for line in f if line.strip()]
    
    # Convert to base module names (without toolchain)
    modules_to_find_base = [extract_module_base(m) for m in modules_to_find_full]
    # Create mapping between base names and full names
    base_to_full = {base: full for base, full in zip(modules_to_find_base, modules_to_find_full)}
    
    # Read the list of easyconfig files to search in
    with open('full_path_eb_files.txt', 'r') as f:
        eb_files = [line.strip() for line in f if line.strip()]
    
    # Dictionary to store the results: module -> list of eb files that define it
    found_modules = {module: [] for module in modules_to_find_full}
    
    # Process each easyconfig file
    for eb_file in eb_files:
        if not os.path.exists(eb_file):
            print(f"Warning: File {eb_file} does not exist, skipping.")
            continue
            
        # Get the filename without the path for output
        filename = os.path.basename(eb_file)
        
        # Extract dependencies from the file
        dependencies = parse_eb_file(eb_file)
        # Convert dependencies to base module names
        dependencies_base = [extract_module_base(d) for d in dependencies]
        
        # Check if any of the dependencies match the modules we're looking for
        for base_module, full_module in zip(modules_to_find_base, modules_to_find_full):
            if base_module in dependencies_base:
                found_modules[full_module].append(filename)
    
    # Output the results
    print("\nResults:")
    for module, eb_files in found_modules.items():
        if eb_files:
            print(f"\n{module} found in:")
            for file in eb_files:
                print(f"  - {file}")
        else:
            print(f"\n{module} not found in any easyconfig file.")

if __name__ == "__main__":
    main()