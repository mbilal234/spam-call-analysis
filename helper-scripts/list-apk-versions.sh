for f in apks/*.apk
do
    $ANDROID_HOME/build-tools/33.0.0-rc4/aapt d badging $f | sed -n "s/^application-label:'\(.*\)'/\1/p"
    # $ANDROID_HOME/build-tools/33.0.0-rc4/aapt d badging $f | grep 'package' | awk -F' ' '{print $2,$3,$4}'
done
