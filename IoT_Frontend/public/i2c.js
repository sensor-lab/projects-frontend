const i2cFields = {
  i2c_unit: 0,
  operation: 'read',
  speed_in_hundred_khz: 1,
  device_address: 0,
  register_address: 0,
  receive_data_length: 0,
  send_data_length: 0,
  send_data: ''
};

var i2cHelpers = {
  changeValue: function(selectObject, field) {

    if (field === 'i2c_unit') {
      i2cFields.i2c_unit = parseInt(selectObject);
    } else if (field === 'operation') {
      i2cFields.operation = selectObject;
      if (selectObject === 'read') {
        document.getElementById("addContent").innerHTML = `
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            Receive Data Length
          </label>
          <input onChange="i2cHelpers.changeValue(this.value, 'receive_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="receive_data_length" type="text" placeholder="0">
        </div>`;
      } else {
        document.getElementById("addContent").innerHTML = `
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            Send Data Length
          </label>
          <input onChange="i2cHelpers.changeValue(this.value, 'send_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="send_data_length" type="text" placeholder="0">
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            Send Data
          </label>
          <input onChange="i2cHelpers.changeValue(this.value, 'send_data')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="send_data" type="text" placeholder="0">
        </div>`;
      }
    } else if (field === 'speed_in_hundred_khz') {
      i2cFields.speed_in_hundred_khz = parseInt(selectObject);
    } else if (field === 'device_address') {
      i2cFields.device_address = parseInt(selectObject)
    } else if (field === 'register_address') {
      i2cFields.register_address = parseInt(selectObject)
    } else if (field === 'receive_data_length') {
      i2cFields.receive_data_length = parseInt(selectObject);
    } else if (field === 'send_data_length') {
      i2cFields.send_data_length = parseInt(selectObject);
    } else if (field === 'send_data') {
      i2cFields.send_data = selectObject;
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
    let request = '/hardware/operation';
    let body;
    if (i2cFields.operation === 'read') {
      body = {
        'event': 'now',
        'actions': [['i2c', i2cFields.i2c_unit, 'read', i2cFields.speed_in_hundred_khz, i2cFields.device_address, i2cFields.register_address, i2cFields.receive_data_length]]
      }
    } else {
      body = {
        'event': 'now',
        'actions': [['i2c', i2cFields.i2c_unit, 'write', i2cFields.speed_in_hundred_khz, i2cFields.device_address, i2cFields.register_address, i2cFields.send_data_length]]
      }
      let send_data = []
      send_data = i2cFields.send_data.split(',').map(Number)
      body['actions'][0] = body['actions'][0].concat(send_data);
    }
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += i2cHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var i2cDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Operation
    </label>
    <select onChange="i2cHelpers.changeValue(this.value, 'operation')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="operation">
      <option>read</option>
      <option>write</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Speed (Hundred KHz)
    </label>
    <select onChange="i2cHelpers.changeValue(this.value, 'speed_in_hundred_khz')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="speed_in_hundred_khz">
      <option>1</option>
      <option>2</option>
      <option>3</option>
      <option>4</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Device Address
    </label>
    <input onChange="i2cHelpers.changeValue(this.value, 'device_address')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="device_address" type="text" placeholder="0">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Register Address
    </label>
    <input onChange="i2cHelpers.changeValue(this.value, 'register_address')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="register_address" type="text" placeholder="0">
  </div>

  <div id="addContent">
    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2">
        Receive Data Length
      </label>
      <input onChange="i2cHelpers.changeValue(this.value, 'receive_data_length')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="receive_data_length" type="text" placeholder="0">
    </div>
  </div>

  <div class="flex items-center justify-between">
    <button onClick="i2cHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

