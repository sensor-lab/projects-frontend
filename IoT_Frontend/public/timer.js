const timerFields = {
  timer: 0,
  unit: 'ms',
  period: 0,
  duration_a: undefined,
  duration_b: undefined,
  duration_c: undefined,
  running_time: undefined
};

var timerHelpers = {
  responseDisplay: function(resp) {
    return `<form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
    <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Response
    </label>
       `
       + resp
       + `</div></form>`;
  },

  changeValue: function(value, field) {

    if (field === 'timer') {
      timerFields.timer = parseInt(value, 10);;
    } else if (field === 'unit') {
      timerFields.unit = value;
    } else if (field === 'period') {
      timerFields.period = parseInt(value, 10);
    } else if (field === 'duration_a') {
      timerFields.duration_a = parseInt(value, 10);;
    } else if (field === 'duration_b') {
      timerFields.duration_b = parseInt(value, 10);;
    } else if (field === 'duration_c') {
      timerFields.duration_c = parseInt(value, 10);;
    } else if (field === 'running_time') {
      timerFields.running_time = parseInt(value, 10);
    }else {
      // Nothing
    }
  },

  errorResponse: function() {
    return `<form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
    <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Please provide valid parameters.
    </label></div></form>`;
  },

  submitClick: async function(object) {
    if (timerFields.duration_a === undefined) {
      document.getElementById('mainResponse').innerHTML += this.errorResponse();
    } else {
      let request = '/hardware/operation'
      let body = {
        'event': 'now',
        'actions': [['pwm', timerFields.timer, 'enabled', timerFields.unit, timerFields.period, timerFields.duration_a, timerFields.duration_b, timerFields.duration_c, timerFields.running_time]]
      }
      try {
        const response = await fetch(request, {
          method: 'post',
          body: JSON.stringify(body)
        }).then(response => response.text())
        .then(response => {
          document.getElementById('mainResponse').innerHTML += timerHelpers.responseDisplay(response);
        });
      } catch(err) {
        console.error(`Error: ${err}`);
      }
    }
  }
}

var timerDisplayer = function()  {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Timer Selection
    </label>
    <select onChange="timerHelpers.changeValue(this.value, 'timer')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="pinSelection">
      <option>0</option>
      <option>1</option>
    </select>
  </div>

  <div class="mb-6">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Time Unit
    </label>
    <select onChange="timerHelpers.changeValue(this.value, 'unit')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="unitSelection">
      <option>us</option>
      <option>ms</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Period
    </label>
    <input onChange="timerHelpers.changeValue(this.value, 'period')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="period" type="text">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Duration for Out Pin A
    </label>
    <input onChange="timerHelpers.changeValue(this.value, 'duration_a')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="duration_a" type="text">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Duration for Out Pin B
    </label>
    <input onChange="timerHelpers.changeValue(this.value, 'duration_b')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="duration_b" type="text">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Duration for Out Pin C
    </label>
    <input onChange="timerHelpers.changeValue(this.value, 'duration_c')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="duration_c" type="text">
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Running Time (10 Millisec Unit)
    </label>
    <input onChange="timerHelpers.changeValue(this.value, 'running_time')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="running_time" type="text">
  </div>

  <div class="flex items-center justify-between">
    <button onClick="timerHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};
