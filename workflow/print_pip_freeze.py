from prefect import task, flow
import subprocess

@flow(name="prin pip freeze", log_prints=True)
def print_pip_freeze():
    try:
        # Run pip freeze and capture the output
        result = subprocess.check_output(["pip", "freeze"], text=True)

        # Print the output
        print("Pip Freeze Output:")
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error while running pip freeze: {e}")
    except FileNotFoundError:
        print("Error: pip is not installed or not found in the system PATH.")
