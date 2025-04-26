# Initial Setup of the LightRAG Environment

This file outlines the steps for setting up the LightRAG environment on a new machine.

## Steps

1. All terminal commands should be run from `C:\Dev\HexMerlin\LightRAG` unless stated otherwise.
2. On GitHub, fork the LightRAG repository to your own account.
3. Create a custom branch named `hex/main` to keep the `main` branch as a mirror of the official upstream repository.
4. Make a clone of the forked repository to your local machine.
5. Bind to the upstream repository:

   ```bash
   git remote add upstream https://github.com/HKUDS/LightRAG.git  
   ```

6. **[CURSOR COMPATIBILITY ONLY]**  
   Create a symbolic link 'env' from the file '.env'.  
   This is necessary since Cursor cannot edit files starting with a dot.  
   Make sure there is a custom instruction for Cursor to always edit 'env' file instead of '.env'.  
   Run terminal as administrator and execute the following command:

   ```bash
   mklink env .env
   ```

7. **[CURSOR COMPATIBILITY ONLY]**
   Add Cursor special instructions as a rule to provide always:

   ```text
   The folder 'my_extensions' is the folder for all files that are not part of the original LightRAG distribution.
   All new files should be created in the folder 'my_extensions' for separatation, to the most possible extent.

   If you want to edit the file '.env' use the file 'env' instead, which is a symbolic link to the file '.env'.
   You cannot edit the file '.env' directly due to Cursor restrictions.
   ```

8. Create a symbolic link for the shared file KNOWLEDGE_GRAPH_SPECIFICATION.md in the Clarity project so it is accessible in this project root LightRAG repository:

   ```bash
   mklink my_extensions\KNOWLEDGE_GRAPH_SPECIFICATION.md ..\..\clarity\KNOWLEDGE_GRAPH_SPECIFICATION.md
   ```

   Add the file `my_extensions\KNOWLEDGE_GRAPH_SPECIFICATION.md` to `.gitignore` (it is version controlled by the Clarity project).

9. Create a Python virtual environment:

   ```bash
   python -m venv .venv
   ```
