import subprocess

def uninstall_requirements(requirements_path="requirements.txt"):
    try:
        with open(requirements_path, "r") as file:
            packages = [line.strip().split("==")[0] for line in file if line.strip() and not line.startswith("#")]
        
        for package in packages:
            print(f"Uninstalling {package}...")
            subprocess.run(["pip", "uninstall", "-y", package], check=False)
        
        print("\nDone uninstalling all packages from requirements.txt")
    except FileNotFoundError:
        print(f"Error: {requirements_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    uninstall_requirements()
