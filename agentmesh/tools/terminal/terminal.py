import platform
import subprocess


class Terminal:
    def open_terminal(self, command):
        system = platform.system()

        try:
            if system == "Windows":
                subprocess.Popen(f'start cmd /k "{command}"', shell=True)
            elif system == "Darwin":
                applescript = f'''
                tell application "Terminal"
                    activate
                    do script "{command}"
                end tell
                '''
                subprocess.run(["osascript", "-e", applescript])
            elif system == "Linux":
                subprocess.Popen(f'gnome-terminal -- bash -c "{command}; exec bash"', shell=True)
            else:
                raise OSError("Unsupported operating system")
            return True
        except Exception as e:
            print(f"Error opening terminal: {str(e)}")
            return False

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
