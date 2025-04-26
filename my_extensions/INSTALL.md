# Initial Setup of the LightRAG Environment

This file outlines the steps for setting up the LightRAG environment on a new machine.

## Steps

1. On GitHub, fork the LightRAG repository to your own account.
2. Create a custom branch named `hex/main` to keep the `main` branch as a mirror of the official upstream repository.
3. Clone the forked repository to your local machine.
4. Bind to the upstream repository:
    ```bash
    git remote add upstream https://github.com/HKUDS/LightRAG.git
    ```
5. FOR CURSOR COMPATIBILITY ONLY: 
Create a symolic link 'env' from the file '.env'
This is necessary, since Cursor cannot edit files starting with a dot.
Make sure there is custom instruction for Cursor to always edit 'env' file instead of '.env'.
Run terminal as administrator and execute the following command:
    ```bash
    mklink env .env
    ```
6. Create a python virtual environment:
    ```bash
    python -m venv .venv
    ```
