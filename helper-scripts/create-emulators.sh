echo "Creating ${1:-10} emulators"

index=0
 
while [ $index -lt ${1:-10} ]
do
    emulator_name="appium_emu_${index}"
    echo "Creating emulator ${index}"

    echo "no" | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n "${emulator_name}" -d pixel_4 --package "system-images;android-30;google_apis_playstore;arm64-v8a"  --tag "google_apis_playstore" --abi "arm64-v8a"

    emulator_base_config=~/.android/avd/${emulator_name}.ini
    mkdir -p ~/.android/avd/${emulator_name}.avd
    emulator_avd_config=~/.android/avd/${emulator_name}.avd/config.ini

    echo $(pwd)

    cp $(pwd)/base_emulator/emulator.ini $emulator_base_config
    cp $(pwd)/base_emulator/emulator.avd/config.ini $emulator_avd_config

    avd_path=~/.android/avd/${emulator_name}.avd

    echo "path=${avd_path}" >> "$emulator_base_config"
    echo "path.rel=avd/${emulator_name}.avd" >> "$emulator_base_config"

    echo "AvdId = ${emulator_name}" >> "$emulator_avd_config"

    index=$(($index+1))

done 

