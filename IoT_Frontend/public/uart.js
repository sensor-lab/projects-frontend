const uartFields = {
  uart_index: 0,
  speed_selection: '9k',
  parity_enabled: 'disabled',
  stop_bit: 1,
  data_size: 8,
  receive_time_out_second: 1,
  receive_data_length: 0,
  send_data_length: 0,
  send_data: ''
};

var uartHelpers = {
  changeValue: function(selectObject, field) {

    if (field === 'uart_index') {
      uartFields.uart_index = parseInt(selectObject);
    } else if (field === 'speed_selection') {
      uartFields.speed_selection = selectObject;
    } else if (field === 'parity_enabled') {
      uartFields.parity_enabled = selectObject;
    } else if (field === 'stop_bit') {
      uartFields.stop_bit = parseInt(selectObject);
    } else if (field === 'data_size') {
      uartFields.data_size = parseInt(selectObject);
    } else if (field === 'receive_time_out_second') {
      uartFields.receive_time_out_second = parseInt(selectObject);
    } else if (field === 'receive_data_length') {
      uartFields.receive_data_length = parseInt(selectObject);
    } else if (field === 'send_data_length') {
      uartFields.send_data_length = parseInt(selectObject);
    } else if (field === 'send_data') {
      uartFields.send_data = selectObject;
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
      'actions': [['uart', uartFields.uart_index, uartFields.speed_selection, uartFields.parity_enabled, uartFields.stop_bit, uartFields.data_size, uartFields.receive_time_out_second, uartFields.receive_data_length, uartFields.send_data_length]]
    }
    let send_data = []
    send_data = uartFields.send_data.split(',').map(Number)
    body['actions'][0] = body['actions'][0].concat(send_data);
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += uartHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var uartDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Uart Module Selection
    </label>
    <select onChange="uartHelpers.changeValue(this.value, 'uart_index')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="uart_index">
      <option>0</option>
      <option>1</option>
      <option>2</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Baud Rate Select
    </label>
    <select onChange="uartHelpers.changeValue(this.value, 'speed_selection')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="speed_selection">
      <option>9k</option>
      <option>38k</option>
      <option>115k</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Parity Enabled
    </label>
    <select onChange="uartHelpers.changeValue(this.value, 'parity_enabled')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="parity_enabled">
      <option>disabled</option>
      <option>even</option>
      <option>odd</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Stop Bit
    </label>
    <select onChange="uartHelpers.changeValue(this.value, 'stop_bit')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="stop_bit">
      <option>1</option>
      <option>2</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Stop Bit
    </label>
    <select onChange="uartHelpers.changeValue(this.value, 'data_size')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="data_size">
      <option>5</option>
      <option>6</option>
      <option>7</option>
      <option>8</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Receive Time Out
    </label>
    <input onChange="uartHelpers.changeValue(this.value, 'receive_time_out_second')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="receive_time_out_second" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Receive Data Length
    </label>
    <input onChange="uartHelpers.changeValue(this.value, 'receive_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="receive_data_length" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Send Data Length
    </label>
    <input onChange="uartHelpers.changeValue(this.value, 'send_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="send_data_length" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Send Data
    </label>
    <input onChange="uartHelpers.changeValue(this.value, 'send_data')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="send_data" type="text" placeholder="0">
  </div>

  <div class="flex items-center justify-between">
    <button onClick="uartHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

