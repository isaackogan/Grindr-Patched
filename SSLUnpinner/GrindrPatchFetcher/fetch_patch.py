import os
import stat
from pathlib import Path
from typing import Optional

import requests


class PatchJarFetcher:
    PROJECT_REPO: str = "isaackogan/Grindr-Spoof-Signature"
    RELEASES_URL: str = f"https://github.com/{PROJECT_REPO}/releases"
    JAR_URL: str = RELEASES_URL + "/download/v%(version)s/revanced-patches-%(version)s.jar"
    JAR_NAME: str = "Signature-Spoofer"
    JAR_QUALIFIED_NAME: str = JAR_NAME + ":%(version)s.jar"

    def __init__(
            self,
            jar_dir: Path = Path(__file__).parent.joinpath("./jars")
    ):
        self._jar_dir: Path = jar_dir

    def download_patch_jar(
            self,
            version: str
    ):
        response = requests.get(self.JAR_URL % {"version": version})

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch v{version} of {self.PROJECT_REPO}. Status Code [{response.status_code}]")

        jar_path: Path = self._jar_dir.joinpath(self.JAR_QUALIFIED_NAME % {"version": version})
        open(jar_path, "wb").write(response.content)
        return jar_path

    def get_jar_path(
            self,
            version: str
    ) -> Path:
        jar_path: Path = self._jar_dir.joinpath(self.JAR_QUALIFIED_NAME % {"version": version})
        latest_version = requests.get(self.RELEASES_URL + "/latest").url.split("/")[-1][1:]
        install_version: Optional[str] = None

        # 1) They are missing the jar
        if not os.path.exists(jar_path):
            print(f"You do not have {version or 'any version'} of {self.PROJECT_REPO} installed. Downloading.")
            install_version = latest_version

        # 2) They have an outdated version
        elif latest_version != version:
            input_str: str = f"There is a newer version {latest_version} of {self.PROJECT_REPO}. Download? (Y/N) "
            install_version = latest_version if input(input_str).lower() == "y" else None

        # 3) They have the right stuff
        else:
            print(f"Found {version} of {self.PROJECT_REPO} installed.")

        # Install it
        if install_version is not None:
            jar_path: Path = self.download_patch_jar(version=install_version)
            os.chmod(jar_path, stat.S_IEXEC)
            print(f"Installed the JAR version {latest_version} of {self.PROJECT_REPO}.")

        return jar_path


if __name__ == '__main__':
    patch_fetcher: PatchJarFetcher = PatchJarFetcher()
    print("Got JAR:", patch_fetcher.get_jar_path(version="4.6.0"))
