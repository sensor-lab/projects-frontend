// Load javascript file dynamically: https://stackoverflow.com/questions/950087/how-do-i-include-a-javascript-file-in-another-javascript-file
const resources = [
  {
    "name": "GPIO",
    "id": "gpio",
    "js_file": "gpio.js",
    "displayer":"gpioDisplayer",
    "jsloaded": false
  },
  {
    "name": "PWM",
    "id": "timer",
    "js_file": "timer.js",
    "displayer": "timerDisplayer",
    "jsloaded": false
  },
  {
    "name": "UART",
    "id": "uart",
    "js_file": "uart.js",
    "displayer": "uartDisplayer",
    "jsloaded": false
  },
  {
    "name": "I2C",
    "id": "i2c",
    "js_file": "i2c.js",
    "displayer": "i2cDisplayer",
    "jsloaded": false
  },
  {
    "name": "SPI",
    "id": "spi",
    "js_file": "spi.js",
    "displayer": "spiDisplayer",
    "jsloaded": false
  },
  {
    "name": "ADC",
    "id": "adc",
    "js_file": "adc.js",
    "displayer": "adcDisplayer",
    "jsloaded": false
  },
  {
    "name": "Clock",
    "id": "clock",
    "js_file": "clock.js",
    "displayer": "clockDisplayer",
    "jsloaded": false
  },
  {
    "name": "File",
    "id": "files",
    "js_file": "files.js",
    "displayer": "filesDisplayer",
    "jsloaded": false
  },
  // {
  //   "name": "Tasks",
  //   "id": "tasks",
  //   "js_file": "tasks.js",
  //   "displayer": "tasksDisplayer",
  //   "jsloaded": false
  // },
  // {
  //   "name": "Firmware Update",
  //   "id": "firmwareupdate",
  //   "js_file": "firmwareupdate.js",
  //   "displayer": "firmwareupdateDisplayer",
  //   "jsloaded": false
  // }
];

const contentDistributor = function(contentId) {
  let resource = resources.find(resource => resource.id === contentId);
  if (resource !== undefined) {

    document.getElementById('mainResponse').innerHTML = '';
    document.getElementById('mainContent').innerHTML = '';
    if (resource.jsloaded === false) {
      let script = document.createElement("script");
      script.src = resource.js_file;
      document.head.appendChild(script);
      script.onload = () => {
        window[resource.displayer]();
      }
      resource.jsloaded = true;
    } else {
      window[resource.displayer]();
    }
  } else {
    throw 'not recognized contentId';
  }
};


const sidebarContent = resources.map((resource) => {
  const onClickFunc = "contentDistributor('" + resource.id + "')";
  const description = resource.name;
  return `
    <li>
      <a href="#" onclick="` + onClickFunc + `">` + description + `</a>
    </li>
  `;
});

window.onload = () => {
  document.getElementById('sidebarContent').innerHTML = sidebarContent.join('');
}

