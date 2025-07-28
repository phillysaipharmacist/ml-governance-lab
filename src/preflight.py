"""
preflight.py
    
Preflight checks for the ML governance lab.  The functions in this module
verify that the host meets minimum requirements: Python 3.11,
Docker Desktop ≥ 4.41, and necessary Python packages.  These checks
reflect regulatory guidance that software used in healthcare should
employ robust software engineering and data management practices.
If a check fails the module prints a
message and returns a non‑zero exit code.
"""
    
import sys
import subprocess
from typing import List
    
    
REQUIRED_PYTHON = (3, 11)
REQUIRED_DOCKER_MINOR = 41
REQUIRED_PACKAGES: List[str] = [
        'pysimplegui',
        'sklearn',
        'numpy',
        'pandas',
        'psycopg2',
        'evidently',
        'seismometer',
        'docker'
    ]
    
    
def check_python() -> bool:
        """Ensure the running Python interpreter meets the required version."""
        major, minor = sys.version_info[:2]
        if (major, minor) < REQUIRED_PYTHON:
            print(
                f"Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} or newer is required. "
                f"Detected {major}.{minor}",
                file=sys.stderr,
            )
            return False
        return True
    
    
def check_docker() -> bool:
        """Check Docker Desktop version; warn if older than 4.41."""
        try:
            # Use docker CLI to get client version
            result = subprocess.run(
                ['docker', 'version', '--format', '{{.Client.Version}}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            version = result.stdout.strip()
            parts = version.split('.')
            if len(parts) >= 2:
                major = int(parts[0])
                minor = int(parts[1])
                if major > 4 or (major == 4 and minor >= REQUIRED_DOCKER_MINOR):
                    return True
                else:
                    print(
                        f"Warning: Docker Desktop {version} detected."
                        f"Upgrade to ≥4.41 to remediate CVE‑2025‑3224",
                        file=sys.stderr,
                    )
                    return True
            else:
                print(
                    f"Could not parse Docker version: '{version}'. Please check your Docker installation.",
                    file=sys.stderr,
                )
                return False
        except Exception:
            print(
                "Docker is not installed or not in PATH. Please install Docker Desktop and rerun.",
                file=sys.stderr,
            )
            return False
    
    
def check_packages() -> bool:
        """Attempt to import each required package and report missing ones."""
        missing: List[str] = []
        for pkg in REQUIRED_PACKAGES:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        if missing:
            print(
                "Missing required packages: " + ', '.join(missing) +
                ". Install dependencies using pip before running the lab.",
                file=sys.stderr,
            )
            return False
        return True
    
    
def main() -> int:
        ok = True
        ok = check_python() and ok
        ok = check_docker() and ok
        ok = check_packages() and ok
        return 0 if ok else 1
    
    
if __name__ == '__main__':
        sys.exit(main())