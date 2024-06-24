from pathlib import Path

from SSLUnpinner.GrindrPatchFetcher.fetch_patch import PatchJarFetcher


class UberAPKJarFetcher(PatchJarFetcher):
    PROJECT_REPO: str = "patrickfav/uber-apk-signer"
    RELEASES_URL: str = f"https://github.com/{PROJECT_REPO}/releases"
    JAR_URL: str = RELEASES_URL + "/download/v%(version)s/uber-apk-signer-%(version)s.jar"
    JAR_NAME: str = "uber-apk-signer-"
    JAR_QUALIFIED_NAME: str = JAR_NAME + "%(version)s.jar"

    def __init__(
            self,
            jar_dir: Path = Path(__file__).parent.joinpath("./jars")
    ):
        super().__init__(jar_dir=jar_dir)


if __name__ == '__main__':
    uber_apk_fetcher: UberAPKJarFetcher = UberAPKJarFetcher()
    print("Got Uber-APK Jar:", uber_apk_fetcher.get_jar_path(version="1.3.0"))
