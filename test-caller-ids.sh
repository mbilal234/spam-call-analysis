current_app_name="showcaller"
rm -rf out/${current_app_name}/screenshots/*
mkdir -p "out/${current_app_name}/screenshots"

declare -a nums
nums=(+18009423767 +16058844130 +18666257291 +18003535920 +18888996650 +13132631171 +18558440114 +18882224227 +18442069035 +18665320423 +18558953393 +18003219637 +18662507212 +18889346489 +18776478552 +17204563720 +18442068573 +18554197365 +18669145806 +18009460332 )
image_allowed="reference_images/${current_app_name}/allowed.png"
image_blocked="reference_images/${current_app_name}/blocked.png"

output_file="out/${current_app_name}/results.csv"
cat /dev/null > $output_file

while read i || [[ -n $i ]];
do
  # Turn off screen
  # adb shell "(dumpsys power | grep mWakefulness=Awake > /dev/null) && input keyevent 26"
  adb  -s emulator-5554 emu gsm call $i
  sleep 1
  filename="out/${current_app_name}/screenshots/${i}.png"
  adb exec-out screencap -p > $filename
  sleep 1
  cancel_output=$(adb -s emulator-5554 emu gsm cancel $i)


  if [[ "$cancel_output" == *"could not cancel this number"* ]]; then
    # Number cancelled by phone. Thus the number is blocked by the phone. We can skip the screenshot comparison
    status="blocked"
  else 

    # Compare the screenshot with the images of the allow and block screen. 
    # We check with which image there is the greatest similarity and use that to decide if the call is blocked or not.  
    allow_diff=$(magick compare -precision 12 -metric ae $filename $image_allowed NULL: 2>&1 > /dev/null)
    block_diff=$(magick compare -precision 12 -metric ae $filename $image_blocked NULL: 2>&1 > /dev/null)

    if [ "$allow_diff" -gt "$block_diff" ]; then
      # echo "Blocked: $allow_diff > $block_diff"
      status="blocked"
    else
      # echo "Allowed: $allow_diff < $block_diff"
      status="allowed"
    fi

  fi

  csv_line="${i},${status}"
  echo $csv_line
  echo $csv_line >> $output_file

  sleep 2
done