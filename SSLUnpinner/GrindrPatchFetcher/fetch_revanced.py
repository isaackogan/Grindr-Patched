from SSLUnpinner.GrindrPatchFetcher.fetch_patch import PatchJarFetcher


class RevancedJarFetcher(PatchJarFetcher):
    PROJECT_REPO: str = "ReVanced/revanced-cli"
    RELEASES_URL: str = f"https://github.com/{PROJECT_REPO}/releases"
    JAR_URL: str = RELEASES_URL + "/download/v%(version)s/revanced-cli-%(version)s-all.jar"
    JAR_NAME: str = "revanced-cli-"
    JAR_QUALIFIED_NAME: str = JAR_NAME + "%(version)s-all.jar"


if __name__ == '__main__':
    revanced_fetcher: RevancedJarFetcher = RevancedJarFetcher()
    print("Got ReVanced:", revanced_fetcher.get_jar_path(version="1.0.0"))