current_app_name="showcaller"
mkdir -p "reference_images/${current_app_name}"

image_allowed="reference_images/${current_app_name}/allowed.png"
image_blocked="reference_images/${current_app_name}/blocked.png"

adb  -s emulator-5554 emu gsm call +31621326032
sleep 1
adb exec-out screencap -p > $image_allowed
sleep 1
adb -s emulator-5554 emu gsm cancel $i +31621326032
sleep 1


adb  -s emulator-5554 emu gsm call +12012000014
sleep 1
adb exec-out screencap -p > $image_blocked
sleep 1
adb -s emulator-5554 emu gsm cancel $i +12012000014
