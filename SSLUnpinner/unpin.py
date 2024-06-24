import os.path
import subprocess
import time
from pathlib import Path

from SSLUnpinner.ApkUnpinTool.unpin_apk import find_pin_file, patch_pin_file, patch_network_security, patch_android_manifest
from SSLUnpinner.GrindrAPKFetcher.fetch_apk import FetchAPKPlatform, fetch_apk, get_apk_path
from SSLUnpinner.GrindrAPKSigner.fetch_uber_signer import UberAPKJarFetcher
from SSLUnpinner.GrindrPatchFetcher.fetch_patch import PatchJarFetcher
from SSLUnpinner.GrindrPatchFetcher.fetch_revanced import RevancedJarFetcher

# CONFIGURE ME
grindr_version: str = "24.2.2"

build_dir: Path = Path(os.path.normpath(Path(__file__).parent.joinpath("../build")))
unsigned_patched_apk_path: Path = build_dir.joinpath("unsigned-patched.apk")
signed_patched_apk_dir: Path = build_dir.joinpath("./signed-patched")

unpinned_apk_path: Path = build_dir.joinpath(f"./spoofed/grindr-spoofed-apk-{grindr_version}.apk")
decompiled_apk_path: Path = build_dir.joinpath("./spoofed-decompiled")

# Get necessary JARs to patch Grindr
revanced_jar_path: Path = RevancedJarFetcher().get_jar_path(version="4.6.0")
revanced_patch_jar_path: Path = PatchJarFetcher().get_jar_path(version="1.0.0")

# Get Uber APK signer
uber_apk_signer_jar_path: Path = UberAPKJarFetcher().get_jar_path(version="1.3.0")

# Make accessible
subprocess.run(f"chmod 777 {revanced_jar_path}", shell=True)
subprocess.run(f"chmod 777 {revanced_patch_jar_path}", shell=True)
subprocess.run(f"chmod 777 {uber_apk_signer_jar_path}", shell=True)

# Step 1) Get the APK
try:
    grindr_apk_path: Path = get_apk_path(version=grindr_version)
except FileNotFoundError:
    grindr_apk_path: Path = fetch_apk(version=grindr_version, platform=FetchAPKPlatform.X86_64_APPLE_DARWIN)

# Step 2) Spoof the APK Signature w/ ReVanced
subprocess.run(
    f'java -jar {revanced_jar_path} '
    f'patch {grindr_apk_path} '
    f'--patch-bundle {revanced_patch_jar_path} '
    f'-o {unpinned_apk_path}',
    shell=True
)

time.sleep(2)

# Step 3) Decompile Spoofed APK
subprocess.run([f"chmod", "777", unpinned_apk_path])
subprocess.run(
    f"apktool d {unpinned_apk_path} -f -o {decompiled_apk_path}",
    shell=True
)

# Step 4) Patch Decompiled Spoofed APK
pin_file: Path = find_pin_file(apk_dir=decompiled_apk_path)
patch_pin_file(pin_file)
patch_network_security(apk_dir=decompiled_apk_path)
patch_android_manifest(apk_dir=decompiled_apk_path)


# Step 5) Recompile the APK
subprocess.run(
    f"apktool b {decompiled_apk_path} -f -o {unsigned_patched_apk_path}",
    shell=True
)

# Step 6) Re-Sign the APK
subprocess.run(
    f"java -jar {uber_apk_signer_jar_path} "
    f"--apks {unsigned_patched_apk_path} "
    f"--out {signed_patched_apk_dir}",
    shell=True
)