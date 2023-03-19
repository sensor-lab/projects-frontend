const timeFields = {
  rtc_id: 0,
  operation: 'read',
  year: 0,
  month: 0,
  day: 0,
  hour: 0,
  minute: 0,
  second: 0
};

var clockHelpers = {
  changeValue: function(selectObject, field) {

    if (field == 'operation') {
      timeFields.operation = selectObject;
      if (selectObject === 'write') {
        document.getElementById('addContent').innerHTML = `
        <div class="flex flex-wrap -mx-3 mb-2">
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Year
            </label>
            <input onChange="clockHelpers.changeValue(this.value, 'year')" class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="year" type="text" placeholder="2020">
          </div>
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Month
            </label>
            <div class="relative">
              <select onChange="clockHelpers.changeValue(this.value, 'month')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="month">
                <option>1</option><option>2</option><option>3</option><option>4</option><option>5</option><option>6</option>
                <option>7</option><option>8</option><option>9</option><option>10</option><option>11</option><option>12</option>
              </select>
            </div>
          </div>
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Day
            </label>
            <input onChange="clockHelpers.changeValue(this.value, 'day')" class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="day" type="text" placeholder="5">
          </div>
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Hour
            </label>
            <input onChange="clockHelpers.changeValue(this.value, 'hour')" class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="hour" type="text" placeholder="13">
          </div>
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Minute
            </label>
            <input onChange="clockHelpers.changeValue(this.value, 'minute')" class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="minute" type="text" placeholder="25">
          </div>
          <div class="w-full md:w-1/3 px-3 mb-6 md:mb-0">
            <label class="block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2">
              Second
            </label>
            <input onChange="clockHelpers.changeValue(this.value, 'second')" class="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:bg-white focus:border-gray-500" id="second" type="text" placeholder="5">
          </div>
        </div>
        `
      } else {
        document.getElementById('addContent').innerHTML = ``
      }
    } else if (field === 'year') {
      if (parseInt(selectObject) < 2000) {
        document.getElementById('mainResponse').innerHTML += this.errorResponse();
      } else {
        timeFields.year = parseInt(selectObject) - 2000;
      }
    } else if (field === 'month') {
      timeFields.month = parseInt(selectObject);
    } else if (field === 'day') {
      timeFields.day = parseInt(selectObject);
    } else if (field === 'hour') {
      timeFields.hour = parseInt(selectObject);
    } else if (field === 'minute') {
      timeFields.minute = parseInt(selectObject)
    } else if (field === 'second') {
      timeFields.second = parseInt(selectObject);
    } else {
      // Nothing
    }
  },

  errorResponse: function() {
    return `<form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
    <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Time has to be larger than 2000
    </label></div></form>`;
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
    if ('read' === timeFields.operation) {
      body = {
        'event': 'now',
        'actions': [['rtc', timeFields.rtc_id, 'read']]
      }
    } else {
      body = {
        'event': 'now',
        'actions': [['rtc', timeFields.rtc_id, 'write', timeFields.year, timeFields.month, timeFields.day, timeFields.hour, timeFields.minute, timeFields.second]]
      }
    }
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += clockHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var clockDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-15 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      System Time
    </label>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Time Operation
    </label>
    <select onChange="clockHelpers.changeValue(this.value, 'operation')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="operation">
      <option>read</option>
      <option>write</option>
    </select>
  </div>

  <div id="addContent">
    <div class="mb-4"></div>
  </div>

  <div class="flex items-center justify-between">
    <button onClick="clockHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

