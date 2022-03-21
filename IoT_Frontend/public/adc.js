const adcFields = {
  module: 0,
  voltage_reference: '5v'
};

var adcHelpers = {
  changeValue: function(selectObject, field) {

    if (field === 'module') {
      adcFields.module = parseInt(selectObject, 10);
    } else if (field === 'voltage_reference') {
      adcFields.voltage_reference = selectObject;
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
    let body = {
      'event': 'now',
      'actions': [['adc', adcFields.module, adcFields.voltage_reference]]
    }
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += adcHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var adcDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      ADC module selection
    </label>
    <select onChange="adcHelpers.changeValue(this.value, 'module')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="module">
      <option>0</option>
      <option>1</option>
      <option>2</option>
      <option>3</option>
      <option>4</option>
      <option>5</option>
      <option>6</option>
      <option>7</option>
      <option>8</option>
      <option>9</option>
      <option>10</option>
      <option>11</option>
      <option>12</option>
      <option>13</option>
      <option>14</option>
      <option>15</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      Voltage Reference
    </label>
    <select onChange="adcHelpers.changeValue(this.value, 'voltage_reference')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="module">
      <option>5v</option>
      <option>1.1v</option>
      <option>2.56v</option>
    </select>
  </div>

  <div class="flex items-center justify-between">
    <button onClick="adcHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>
  </form>
  `;
};

