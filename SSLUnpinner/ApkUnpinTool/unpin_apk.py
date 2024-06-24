import re
import textwrap
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

PIN_STRINGS = ["grindr.mobi", "sslPinSite"]


def find_pin_file(apk_dir: Path) -> Path:
    print("Searching for pin file...")
    if not apk_dir.exists() and apk_dir.is_dir():
        raise FileNotFoundError("APK dir not found or is not a directory!")

    found_files: List[Path] = []

    # Walk through all files in the directory recursively
    for file in apk_dir.rglob('*'):
        if file.is_file() and file.name.endswith(".smali"):
            try:
                content = open(file, 'r').read()
                if all(s in content for s in PIN_STRINGS):
                    found_files.append(file)
            except Exception as e:
                print(f"Could not read {file}: {e}")

    if len(found_files) < 0:
        raise FileNotFoundError("Failed to find the pin site modification file")

    if len(found_files) > 1:
        raise FileExistsError("Found more than 1 pin site file. Should only be one.")

    return found_files[0]


def patch_pin_file(pin_file: Path) -> None:
    contents: str = open(pin_file, 'r').read()

    # Flip the SSL pin OkHttp bool off
    new_contents: str = re.sub(
        r".line\s+18\s+const/4\s+v0,\s+0x1",
        ".line 18\n    const/4 v0, 0x0",
        contents,
    )

    # Overwrite file
    open(pin_file, 'w').write(new_contents)


def patch_network_security(apk_dir: Path) -> None:
    with open(apk_dir.joinpath("./res/xml/network_security_config.xml"), 'w') as f:
        f.write(
            textwrap.dedent(
                """
                <?xml version="1.0" encoding="utf-8"?>
                <network-security-config>
                    <debug-overrides>
                        <trust-anchors>
                            <!-- Trust user added CAs while debuggable only -->
                            <certificates src="user" />
                            <certificates src="system" />
                        </trust-anchors>
                    </debug-overrides>
                
                    <base-config cleartextTrafficPermitted="true">
                        <trust-anchors>
                            <certificates src="system" />
                            <certificates src="user" />
                        </trust-anchors>
                    </base-config>
                </network-security-config>
                """
            ).strip()
        )


def patch_android_manifest(apk_dir: Path) -> None:
    file_path: Path = apk_dir.joinpath("AndroidManifest.xml")

    # Load and parse the AndroidManifest.xml file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the namespace prefix often used in Android XML files
    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    # Find the application tag. Assuming there is exactly one <application> tag
    application = root.find('application', ns)

    # Check if the application tag exists and modify it
    if application is not None:
        # Add the new property, handling namespaces properly
        application.set(f"{{{ns['android']}}}networkSecurityConfig", "@xml/network_security_config")
    else:
        raise RuntimeError("No <application> tag found in the AndroidManifest.xml.")

    # Write the modified XML back to the file
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

