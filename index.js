// javascript

const wdio = require("webdriverio");
const assert = require("assert");

const opts = {
    path: '/wd/hub',
    port: 4723,
    capabilities: {
        platformName: "Android",
        platformVersion: "12",
        deviceName: "Pixel_4_API_30",
        avd: "Pixel_4_API_30",
        // app: "/Users/christiaanvanluik/Documents/Development/appium-playground/ApiDemos-debug.apk",
        // appPackage: "io.appium.android.apis",
        // appActivity: ".view.TextFields",
        automationName: "UiAutomator2"
    }
};

const caller_ids = [
    8009423767,
    6058844130,
    8666257291,
    8003535920,
    8888996650,
    3132631171,
    8558440114,
    8882224227,
    8442069035,
    8665320423,
    8558953393,
    8003219637,
    8662507212,
    8889346489,
    8776478552,
    7204563720,
    8442068573,
    8554197365,
    8669145806,
    8009460332,
];


async function main() {


    const client = await wdio.remote(opts);

    for (let index = 0; index < caller_ids.length; index++) {
        const element = caller_ids[index];
        let callerid = element.toString();

        client.gsmCall(callerid.toString(), 'call');

        await sleep(1500);

        // let screenshot = client.takeScreenshot();
        client.takeScreenshot().then(
            function(image, err) {
                require('fs').writeFile('out/app1-'+ callerid.toString() +'.png', image, 'base64', function(err) {
                    console.log(err);
                });
            }
        );
        
        client.gsmCall(callerid.toString(), 'cancel');
    }


}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
} 

main();
