    <##
        bootstrap/setup.ps1

        This PowerShell script bootstraps a local‑only machine learning governance
        environment on Windows.  It installs or upgrades core tools using
        Chocolatey in an idempotent manner.  The script checks for the
        presence of Chocolatey and installs it if missing.  Packages such as
        Git, Python 3.11, the pip‑tools suite, and Docker Desktop are then
        installed or upgraded.  Docker Desktop version 4.41 or later is
        required because earlier builds contained a local privilege
        escalation (CVE‑2025‑3224) that was fixed in the 4.41 release
        notes. The script exits quietly when
        prerequisites are already satisfied.
    ##>

    [CmdletBinding()]
    param()

    function Ensure-Chocolatey {
        # Check for Chocolatey.  Chocolatey’s installation script only runs when
        # the choco executable is absent.  This follows the idempotent install
        # pattern described in the Chocolatey documentation.
        if (-not (Get-Command choco.exe -ErrorAction SilentlyContinue)) {
            Write-Host "Installing Chocolatey…"
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        } else {
            Write-Host "Chocolatey is already installed."
        }
    }

    function Ensure-Package {
        param(
            [string]$Name,
            [string]$Version,
            [string]$PackageName = $Name
        )
        # Query installed package version using choco.  If not installed or
        # version differs, install/upgrade.  Chocolatey installs new versions
        # while leaving existing software untouched when the desired version is
        # already present.
        $pkg = choco list --local-only --exact $PackageName | Select-String -Pattern '^$PackageName '
        if ($pkg) {
            if ($pkg.ToString().Contains($Version)) {
                Write-Host "$PackageName $Version already installed."
            } else {
                Write-Host "Upgrading $PackageName to $Version…"
                choco upgrade $PackageName --version $Version -y --no-progress
            }
        } else {
            Write-Host "Installing $PackageName $Version…"
            choco install $PackageName --version $Version -y --no-progress
        }
    }

    function Require-PythonVersion {
        param(
            [version]$RequiredVersion
        )
        # Compare the installed Python version.  If not present or too low, exit
        # with an error so the user can upgrade.  Python 3.11 is required for
        # this lab.
        try {
            $output = & python --version 2>&1
            if ($output -match 'Python ([0-9]+)\.([0-9]+)\.([0-9]+)') {
                $maj = [int]$Matches[1]
                $min = [int]$Matches[2]
                $patch = [int]$Matches[3]
                $installed = New-Object System.Version($maj,$min,$patch)
                if ($installed -lt $RequiredVersion) {
                    Write-Error "Python $RequiredVersion or newer is required. Detected $installed."
                    exit 1
                } else {
                    Write-Host "Python $installed detected."
                }
            } else {
                Write-Error "Unable to determine Python version."
                exit 1
            }
        } catch {
            Write-Error "Python is not installed or not found in PATH."
            exit 1
        }
    }

    function Check-DockerVersion {
        # Extract the Docker Desktop client version.  The 4.41 release notes
        # identify a privilege escalation CVE fixed in that release.
        # If the installed version is lower than 4.41, prompt the user to
        # upgrade.
        try {
            $verString = & docker version --format '{{.Client.Version}}'
            if ($verString) {
                $parts = $verString.Split('.')
                $major = [int]$parts[0]
                $minor = [int]$parts[1]
                if ($major -gt 4 -or ($major -eq 4 -and $minor -ge 41)) {
                    Write-Host "Docker Desktop version $verString detected."
                } else {
                    Write-Warning "Docker Desktop $verString is out of date. Please upgrade to >= 4.41 to remediate CVE‑2025‑3224."
                }
            } else {
                Write-Warning "Unable to determine Docker version. Ensure Docker Desktop is installed."
            }
        } catch {
            Write-Warning "Docker is not installed or not found in PATH."
        }
    }

    function Main {
        Ensure-Chocolatey
        # Install core packages.  Versions pinned for reproducibility.  You may
        # adjust versions but maintain Python 3.11 compatibility.
        Ensure-Package -Name 'python' -Version '3.11.5' -PackageName 'python'
        Ensure-Package -Name 'git' -Version '2.44.0' -PackageName 'git'
        Ensure-Package -Name 'pip-tools' -Version '7.0.0' -PackageName 'pip-tools'
        Ensure-Package -Name 'docker-desktop' -Version '4.41.0' -PackageName 'docker-desktop'

        # Verify Python version
        Require-PythonVersion -RequiredVersion ([version]'3.11.0')

        # Check Docker version after installation
        Check-DockerVersion

        Write-Host "Bootstrap complete."
    }

    Main