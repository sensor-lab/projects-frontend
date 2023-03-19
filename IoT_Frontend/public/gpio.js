const gpioFields = {
  pin: 0,
  mode: 'input',
  pullUpResister: 1,
  outputLevel: 1
};

var gpioHelpers = {
  changeValue: function(selectObject, field) {

    if (field === 'mode') {
      if (selectObject === 'input') {
        document.getElementById("addContent").innerHTML = `
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            Pull Up Resistor
          </label>
          <select onChange="gpioHelpers.changeValue(this.value, 'puResistor')"  class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="pinSelection">
            <option>Enable</option>
            <option>Disable</option>
          </select>
        </div>`;
        gpioFields.mode = 'input';
      } else {
        document.getElementById("addContent").innerHTML = `
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            Output Voltage
          </label>
          <select onChange="gpioHelpers.changeValue(this.value, 'outputLevel')"  class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="pinSelection">
            <option>High</option>
            <option>Low</option>
          </select>
        </div>`;
        gpioFields.mode = 'output';
      }
    } else if (field === 'Pin') {
      gpioFields.pin = parseInt(selectObject, 10);
    } else if (field === 'puResistor') {
      if (selectObject === 'Disable') {
        gpioFields.pullUpResister = 0;
      } else {
        gpioFields.pullUpResister = 1;
      }
    } else if (field === 'outputLevel') {
      if (selectObject === 'Low') {
        gpioFields.outputLevel = 0;
      } else {
        gpioFields.outputLevel = 1;
      }
    } else {
      // Nothing
    }
  },

  responseDisplay: function(resp) {
    return `<form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
    <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Response
    </label>
       `
       + resp
       + `</div></form>`
  },

  submitClick: async function(object) {
    let request = '/hardware/operation';
    let body;
    if ('output' === gpioFields.mode) {
      body = {
        'event': 'now',
        'actions': [['gpio', gpioFields.pin, gpioFields.mode, gpioFields.outputLevel]]
      }
    } else {
      body = {
        'event': 'now',
        'actions': [['gpio', gpioFields.pin, gpioFields.mode, gpioFields.pullUpResister]]
      }
    }
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += gpioHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var gpioDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Pin
    </label>
    <input onChange="gpioHelpers.changeValue(this.value, 'Pin')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="Pin" type="text" placeholder="1">
  </div>

  <div class="mb-6">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Mode Selection
    </label>
    <select class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="modeSelection" onChange="gpioHelpers.changeValue(this.value, 'mode')">
      <option>input</option>
      <option>output</option>
    </select>
  </div>

  <div id="addContent">
    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2">
        Pull Up Resistor
      </label>
      <select onChange="gpioHelpers.changeValue(this.value, 'puResistor')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="pinSelection">
        <option>Enable</option>
        <option>Disable</option>
      </select>
    </div>
  </div>

  <div class="flex items-center justify-between">
    <button onClick="gpioHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

