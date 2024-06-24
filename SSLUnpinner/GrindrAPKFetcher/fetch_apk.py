import enum
import logging
import os.path
import stat
import subprocess
from pathlib import Path
from typing import Optional

import requests
from requests import Response

FETCHER_BINARY_PATH: str = "https://github.com/rabilrbl/downapk/releases/download/%(version)s/%(platform)s"
GRINDR_PACKAGE: str = "com.grindrapp.android"


class FetchAPKPlatform(str, enum.Enum):
    """
    Available binaries for the APK fetching tool

    """

    AARCH_64_APPLE_DARWIN = "downapk-aarch64-apple-darwin"
    AARCH_64_LINUX_ANDROID = "downapk-arch64-linux-android"
    AARCH_64_PC_WINDOWS_MSVC = "downapk-arch64-pc-windows-msvc.exe"
    AARCH_64_UNKNOWN_LINUX_GNU = "downapk-arch64-unknown-linux-gnu"
    ARMV7_LINUX_ANDROIDABI = "downapk-armv7-linux-androideabi"
    ARMV7_UNKNOWN_LINUX_GNUEABIHF = "downapk-armv7-unknown-linux-gnueabihf"
    I686_PC_WINDOWS_MSVC = "downapk-i686-pc-windows-msvc.exe"
    I686_UNKNOWN_LINUX_GNU = "downapk-i686-unknown-linux-gnu"
    X86_64_APPLE_DARWIN = "downapk-x86_64-apple-darwin"
    X86_64_LINUX_ANDROID = "downapk-x86_64-linux-android"
    X86_64_PC_WINDOWS_MSVC = "downapk-x86_64-pc-windows-msvc.exe"
    X86_64_UNKNOWN_LINUX_GNU = "downapk-x86_64-unknown-linux-gnu"


def check_latest_version() -> str:
    """
    Grab the latest release off GitHub
    :return: Latest release version number

    """

    return requests.get("https://github.com/rabilrbl/downapk/releases/latest").url.split("/")[-1]


def get_binary_path(binary_dir: Path, platform: FetchAPKPlatform) -> Optional[Path]:
    if not binary_dir.is_dir():
        raise NotADirectoryError("Binary directory must be a directory!")

    matches: list[str] = [
        name for name in os.listdir(binary_dir) if name.startswith(f"{platform.value}")
    ]

    if len(matches) > 1:
        logging.error("Multiple JARs found. Picking the first one.")

    return binary_dir.joinpath(matches[0]) if len(matches) > 0 else None


def get_current_version(binary_dir: Path, platform: FetchAPKPlatform) -> Optional[str]:
    """
    Grab the currently installed binary version

    :param binary_dir: Directory containing the binary to check
    :param platform: Platform to check
    :return: Binary version number

    """

    current_version_path = get_binary_path(binary_dir, platform)

    return str(current_version_path).split(":")[1] if current_version_path else None


def download_version(binary_dir: Path, platform: FetchAPKPlatform, version: str) -> Path:
    response: Response = requests.get(FETCHER_BINARY_PATH % {"version": version, "platform": platform.value})

    if response.status_code == 404:
        raise ValueError(f"Could not find the version {version} for {platform.value} on GitHub")

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the version {version} for {platform.value}")

    binary_data: bytes = response.content
    output_path: Path = binary_dir.joinpath(f"./{platform.value}:{version}")

    with open(output_path, 'wb') as file:
        file.write(binary_data)

    return output_path


def get_binary(
        platform: FetchAPKPlatform,
        binary_dir: Path
) -> Path:
    """
    Run the binary fetching tool

    :param platform: The platform you're on
    :param binary_dir: Where the binary should be checked for & stored in
    :return: The path to the binary

    """

    binary_path: Optional[Path] = get_binary_path(binary_dir, platform)
    current_version: Optional[str] = get_current_version(binary_dir, platform)
    latest_version: str = check_latest_version()
    install_binary: bool = False

    if current_version is None:
        print("You do not have the APK-fetching binary! This will need to be installed.")
        install_binary = True
    elif current_version != latest_version:
        install_binary = input(
            f"There is a new version {latest_version}. Do you want the latest? (Y/N) ").lower() == "y"
    else:
        print(f"Currently have the latest version {latest_version} for {platform.value}")

    if install_binary:
        binary_path: Path = download_version(platform=platform, binary_dir=binary_dir, version=latest_version)
        os.chmod(binary_path, stat.S_IEXEC)
        print(f"Installed the APK fetcher version {latest_version} for {platform.value}")

    return binary_path


def fetch_apk(
        version: str,
        platform: FetchAPKPlatform,
        apk_dir: Path = Path(__file__).parent.joinpath("./apks"),
        binary_dir: Path = Path(__file__).parent.joinpath("./binaries")
) -> Path:
    """
    Fetch the Grindr APK from TikTok

    :param version: APK version to fetch
    :param platform: Platform to select the correct binary
    :param apk_dir: Output FP for the APK
    :param binary_dir: Where to put the binary for APK fetching
    :return: The output path of the APK

    """

    if not os.path.isdir(apk_dir):
        raise NotADirectoryError("Output directory must be a directory!")

    binary_path: Path = get_binary(
        platform=platform,
        binary_dir=binary_dir
    )

    command: list[str] = [
        binary_path,
        "--package-id", GRINDR_PACKAGE,
        "--version-code", version,
        '--apk-type', "apk",
        "-d", "one",
        "-i", "1",
        "-s", "1",
        "-o", str(apk_dir.absolute()),
    ]

    print("Downloading APK...")
    print("Executing: ", " ".join([str(i) for i in command]))

    result = subprocess.run(command)

    if result.returncode != 0:
        raise Exception(f"Subprocess failed with return code {result.returncode} and error message: {result.stderr}")

    # Return the path of the generated APK
    return get_apk_path(
        apk_dir=apk_dir,
        version=version
    )


def get_apk_path(
        version: str,
        apk_dir: Path = Path(__file__).parent.joinpath("./apks")
) -> Path:
    """
    Fetch the Grindr APK from APKDown

    :param apk_dir: Where to put Grindr / where it is
    :param version: The APK version to fetch
    :return: The path to the APK

    """

    for file in os.listdir(apk_dir):
        if not file.endswith(".apk"):
            continue

        if not file.startswith(GRINDR_PACKAGE):
            continue

        if version not in file:
            continue

        print(f"Found {version} of Grindr APK installed.")
        return Path(apk_dir.joinpath(file))

    raise FileNotFoundError("Could not find the specific APK!")
