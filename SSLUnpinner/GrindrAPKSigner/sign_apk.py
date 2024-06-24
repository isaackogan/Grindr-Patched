import subprocess
from pathlib import Path

jar_dir: Path = Path(__file__).parent.joinpath("./jars")

# /Users/isaackogan/Documents/AndroidStudioProjects/GrindrSSLUnpinned/SSLUnpinner/GrindrAPKSigner/jars/uber-apk-signer-1.3.0.jar
# /Users/isaackogan/Documents/AndroidStudioProjects/GrindrSSLUnpinned/SSLUnpinner/GrindrAPKSigner/jars/uber-apk-signer-1.1.0.jar

# /Users/isaackogan/Documents/AndroidStudioProjects/GrindrSSLUnpinned/build/patched-unsigned.apk
# /Users/isaackogan/Documents/AndroidStudioProjects/GrindrSSLUnpinned/build/patched-unsigned.apk

apk_signer_jar: Path = jar_dir.joinpath("uber-apk-signer-1.1.0.jar").absolute()

print(apk_signer_jar)


def sign_apk(apk_path: Path) -> None:
    print(apk_path)
    subprocess.run([f"chmod", "777", apk_signer_jar])

    subprocess.run(
        [apk_signer_jar, f"--apks", apk_path, "--out", "apk-signed.apk"],
        shell=True
    )
