const spiFields = {
  spi_index: 0,
  speed_level: 0,
  cs_pin: 0,
  sample_mode: 'lr',
  bit_orientation: 'msb',
  receive_data_length: 0,
  send_data_length: 0,
  data_to_send: ''
};

var spiHelpers = {
  changeValue: function(selectObject, field) {

    if (field === 'spi_index') {
      spiFields.spi_index = parseInt(selectObject, 10);
    } else if (field === 'speed_level') {
      spiFields.speed_level = parseInt(selectObject, 10);
    } else if (field === 'cs_pin') {
      spiFields.cs_pin = parseInt(selectObject, 10);
    } else if (field === 'sample_mode') {
      spiFields.sample_mode = selectObject;
    } else if (field === 'bit_orientation') {
      spiFields.bit_orientation = selectObject;
    } else if (field === 'receive_data_length') {
      spiFields.receive_data_length = parseInt(selectObject, 10);
    } else if (field === 'send_data_length') {
      spiFields.send_data_length = parseInt(selectObject);
    } else if (field === 'data_to_send') {
      spiFields.data_to_send = selectObject;
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

  _objectWithoutProperties: function(obj, keys) {
    var target = {};
    for (var i in obj) {
      if (keys.indexOf(i) >= 0) continue;
      if (!Object.prototype.hasOwnProperty.call(obj, i)) continue;
      target[i] = obj[i];
    }
    return target;
  },

  submitClick: async function(object) {
    let request = '/hardware/operation'
    let body = {
      'event': 'now',
      'actions': [['spi', spiFields.spi_index, spiFields.speed_level, spiFields.cs_pin, spiFields.sample_mode, spiFields.bit_orientation, spiFields.receive_data_length, spiFields.send_data_length]]
    }
    let send_data = []
    send_data = spiFields.data_to_send.split(',').map(Number)
    body['actions'][0] = body['actions'][0].concat(send_data);
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += spiHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var spiDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Speed Level
    </label>
    <select onChange="spiHelpers.changeValue(this.value, 'speed_level')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="speed_level">
      <option>0</option>
      <option>1</option>
      <option>2</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      CS Pin
    </label>
    <input onChange="spiHelpers.changeValue(this.value, 'cs_pin')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="cs_pin" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Sample Mode
    </label>
    <select onChange="spiHelpers.changeValue(this.value, 'sample_mode')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="sample_mode">
      <option>lr</option>
      <option>tf</option>
      <option>lf</option>
      <option>tr</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Bit Orientation
    </label>
    <select onChange="spiHelpers.changeValue(this.value, 'bit_orientation')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="bit_orientation">
      <option>msb</option>
      <option>lsb</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Receive Data Length
    </label>
    <input onChange="spiHelpers.changeValue(this.value, 'receive_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="receive_data_length" type="text" placeholder="0">
  </div>


  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Send Data Length
    </label>
    <input onChange="spiHelpers.changeValue(this.value, 'send_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="send_data_length" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Send Data
    </label>
    <input onChange="spiHelpers.changeValue(this.value, 'data_to_send')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="data_to_send" type="text" placeholder="0">
  </div>

  <div class="flex items-center justify-between">
    <button onClick="spiHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

