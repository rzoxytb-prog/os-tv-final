#!/usr/bin/env bash
# Construit RoseOS.apk sans Gradle : aapt2 -> javac -> d8 -> zipalign -> apksigner.
# Il faut un JDK 17 et le SDK Android (build-tools 34, platform android-34).
set -euo pipefail
cd "$(dirname "$0")"

# --- Outils
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if [ -z "$SDK" ]; then
  for d in "$HOME/Library/Android/sdk" "$HOME/Android/Sdk" /opt/homebrew/share/android-commandlinetools \
           /usr/local/share/android-commandlinetools /usr/lib/android-sdk; do
    if [ -d "$d/build-tools" ]; then SDK="$d"; break; fi
  done
fi
[ -n "$SDK" ] && [ -d "$SDK/build-tools" ] || { echo "SDK Android introuvable : installe-le et définis ANDROID_HOME."; exit 1; }
if [ -d "$SDK/build-tools/34.0.0" ]; then BT="$SDK/build-tools/34.0.0"; else BT="$SDK/build-tools/$(ls "$SDK/build-tools" | sort -V | tail -1)"; fi
if [ -f "$SDK/platforms/android-34/android.jar" ]; then AJ="$SDK/platforms/android-34/android.jar"
else AJ="$(ls -d "$SDK"/platforms/android-*/android.jar 2>/dev/null | sort -V | tail -1 || true)"; fi
[ -f "${AJ:-}" ] || { echo "Plateforme Android introuvable. Lance : sdkmanager \"platforms;android-34\""; exit 1; }
JAVAC="${JAVA_HOME:+$JAVA_HOME/bin/}javac"
KEYTOOL="${JAVA_HOME:+$JAVA_HOME/bin/}keytool"
command -v "$JAVAC" >/dev/null 2>&1 || { echo "JDK introuvable. Installe un JDK 17 et définis JAVA_HOME."; exit 1; }
BOOT="$AJ"; [ -f "$BT/core-lambda-stubs.jar" ] && BOOT="$AJ:$BT/core-lambda-stubs.jar"

# --- Build (l'interface web/ sert aussi de dossier "assets" Android)
rm -rf out && mkdir -p out/gen out/classes
"$BT/aapt2" compile --dir app/res -o out/res.zip
"$BT/aapt2" link -o out/base.apk -I "$AJ" --manifest app/AndroidManifest.xml --java out/gen out/res.zip \
  --min-sdk-version 24 --target-sdk-version 34 -A web
"$JAVAC" -nowarn -Xlint:-options -source 8 -target 8 -bootclasspath "$BOOT" -classpath "$AJ" \
  -encoding UTF-8 -d out/classes $(find app/src out/gen -name '*.java')
"$BT/d8" --release --min-api 24 --lib "$AJ" --output out $(find out/classes -name '*.class')
(cd out && zip -qj base.apk classes.dex)
"$BT/zipalign" -f -p 4 out/base.apk out/aligned.apk

# --- Signature avec ta propre clé (créée une fois : garde roseos.keystore, les mises à jour doivent utiliser la même)
if [ ! -f roseos.keystore ]; then
  "$KEYTOOL" -genkeypair -keystore roseos.keystore -alias roseos -keyalg RSA -keysize 2048 -validity 20000 \
    -storepass roseos123 -keypass roseos123 -dname "CN=Rose OS" >/dev/null 2>&1
fi
"$BT/apksigner" sign --ks roseos.keystore --ks-pass pass:roseos123 --key-pass pass:roseos123 --out RoseOS.apk out/aligned.apk
echo "Built RoseOS.apk ($(du -h RoseOS.apk | cut -f1)). Installer : adb install -r RoseOS.apk"
