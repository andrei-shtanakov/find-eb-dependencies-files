## EasyBuild Toolchain Dependencies

In the EasyBuild system, toolchain relationships are quite complex but follow certain rules. When using the `foss-2023a` module, dependencies can indeed belong to both `GCC-12.3.0` and `GCCcore-12.3.0`, which is determined by the toolchain hierarchy.

`foss` is a metatoolchain that typically includes:
- `GCC` (compiler)
- `OpenMPI` (MPI implementation)
- Math libraries (e.g., OpenBLAS, FFTW, ScaLAPACK)

When searching for dependencies, EasyBuild follows these rules:

1. First, it checks for dependencies with the same toolchain as the main module (`foss-2023a`)
2. Then it looks for dependencies with the base compiler on which `foss` is built (i.e., `GCC-12.3.0`)
3. Next, it searches in `GCCcore-12.3.0` for components that don't use features of external compilers
4. Finally, it looks for "toolchainless" modules (`system` or modules with `-system` suffix)

In `foss-2023a`, dependencies are distributed approximately as follows:
- Components using MPI (e.g., specialized libraries) → `foss-2023a`
- Components that only need the GCC compiler → `GCC-12.3.0`
- Basic libraries that can be compiled with any C/C++ compiler → `GCCcore-12.3.0`

The dependency search order is determined by the `robot_path` parameter and the `EASYBUILD_ROBOT_PATHS` environment variable, which specify directories in order of priority for searching .eb files.

If you're developing your own module based on `foss-2023a`, you should follow the principle: use the most basic toolchain sufficient for the component (to avoid unnecessary recompilations and maximize reuse).

## Easyconfig File Naming Rules

The naming rules for easyconfig files in EasyBuild have a specific structure that reflects the main characteristics of the module. The standard file name format looks like this:

```
<name>-<version>[-<toolchain>][-<suffix>].eb
```

Let's break down each component:

1. **Name** - the name of the software package (e.g., `GROMACS`, `Python`)
2. **Version** - the package version (e.g., `2023.2`, `3.10.8`)
3. **Toolchain** - the toolchain used with its version, enclosed in hyphens:
   - `-<toolchain_name>-<toolchain_version>` (e.g., `-foss-2023a`, `-GCC-12.3.0`)
   - If the package doesn't require compilation or uses system libraries, the toolchain may be absent
   - For a "toolchainless" package, `-system` can be used

4. **Suffix** - an optional part that indicates configuration specifics:
   - May indicate special build settings (`-CUDA-11.8.0`)
   - Specific Python versions (`-Python-3.10.8`)
   - Configuration features (`-bare`, `-MPI-4.1.5`, `-threaded`)

Examples of correct easyconfig file names:

- `Python-3.10.8-GCCcore-12.3.0.eb` - Python 3.10.8, built with GCCcore 12.3.0
- `GROMACS-2023.2-foss-2023a.eb` - GROMACS 2023.2, built with the foss 2023a toolchain
- `GROMACS-2023.2-foss-2023a-CUDA-11.8.0.eb` - GROMACS with CUDA support
- `OpenSSL-1.1.1u-GCCcore-12.3.0.eb` - OpenSSL built with GCCcore
- `LLVM-16.0.0-GCCcore-12.3.0.eb` - LLVM built using GCCcore
- `hwloc-2.9.1-GCCcore-12.3.0.eb` - hwloc built using GCCcore
- `Perl-5.36.1-GCCcore-12.3.0-minimal.eb` - minimal Perl build

It's important that the file name exactly matches the values in the easyconfig file itself:
- `name` should correspond to the first part of the file name
- `version` should match the version in the file name
- `toolchain` should match the specified toolchain
- If there's a suffix, it should be reflected in the corresponding parameters within the file

Following these naming rules is necessary for the EasyBuild system to work correctly and ensure module compatibility.

## Easyconfig File Organization in the File System

In EasyBuild, easyconfig files are organized in the file system according to a specific structure that facilitates searching and configuration management. A typical organization looks like this:

1. **Main easyconfigs directory**:
   - Usually located in the EasyBuild installation path, for example: `/path/to/easybuild/easyconfigs/`
   - There may also be a separate user directory: `$HOME/.local/easybuild/easyconfigs/`

2. **Subdirectory structure**:
   - First level - directory corresponding to the first letter of the package name: `/path/to/easyconfigs/g/` for GROMACS
   - Second level - directory with the full package name: `/path/to/easyconfigs/g/GROMACS/`
   - Inside the package folder are all easyconfig files for different versions and toolchains

Example of a complete structure:
```
/path/to/easyconfigs/
├── b/
│   ├── Bison/
│   │   ├── Bison-3.8.2-GCCcore-12.3.0.eb
│   │   └── Bison-3.8.2-GCCcore-13.2.0.eb
│   └── Boost/
│       ├── Boost-1.82.0-GCC-12.3.0.eb
│       └── Boost-1.82.0-foss-2023a.eb
├── g/
│   ├── GCC/
│   │   ├── GCC-12.3.0.eb
│   │   └── GCC-13.2.0.eb
│   └── GROMACS/
│       ├── GROMACS-2023.2-foss-2023a.eb
│       └── GROMACS-2023.2-foss-2023a-CUDA-11.8.0.eb
├── o/
│   └── OpenMPI/
│       └── OpenMPI-4.1.5-GCC-12.3.0.eb
└── p/
    └── Python/
        ├── Python-3.10.8-GCCcore-12.3.0.eb
        └── Python-3.11.3-GCCcore-12.3.0.eb
```

Important aspects of organization:

- The EasyBuild **search path** (robot path) typically includes these directories to automatically find dependencies
- The `--robot` parameter tells EasyBuild to look for dependencies in certain paths
- The `EASYBUILD_ROBOT_PATHS` environment variable can contain a list of directories to search
- Developers can create their own file structures, but following the standard structure makes integration with EasyBuild tools easier

When creating your own easyconfig files, it's recommended to adhere to this structure for more convenient management and compatibility with EasyBuild tools.
