const fileFields = {
  file_index: 0,
  operation: 'read',
  file_name: '',
  content: ''
};

var fileHelpers = {
  changeValue: function(selectObject, field) {
    if (field === 'operation') {
      fileFields.operation = selectObject
      if (operation === 'read') {
        document.getElementById('addContent').innerHTML = ``
      } else {
        document.getElementById('addContent').innerHTML = `
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            File Content
          </label>
          <textarea onChange="fileHelpers.changeValue(this.value, 'content')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="content" type="text" placeholder="0"></textarea>
        </div>`
      }
    } else if (field == 'file_name') {
      fileFields.file_name = selectObject
    } else if (field == 'content') {
      fileFields.content = selectObject
    } else {
      // Do nothing
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
    let request = '/hardware/operation'
    let body
    if (fileFields.operation === 'read') {
      body = {
        'event': 'now',
        'actions': [['file', fileFields.file_index, 'read', fileFields.file_name]]
      }
    } else {
      body = {
        'event': 'now',
        'actions': [['file', fileFields.file_index, 'write', fileFields.file_name, fileFields.content]]
      }
    }
    try {
      const response = await fetch(request, {
        method: 'post',
        body: JSON.stringify(body)
      }).then(response => response.text())
      .then(response => {
        document.getElementById('mainResponse').innerHTML += fileHelpers.responseDisplay(response);
      });
    } catch(err) {
      console.error(`Error: ${err}`);
    }
  }
}

var filesDisplayer = function () {

  document.getElementById("mainContent").innerHTML = `
  <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 ml-5">
  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      File Operation
    </label>
    <select onChange="fileHelpers.changeValue(this.value, 'operation')" class="block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500 text-sm" id="operation">
      <option>read</option>
      <option>write</option>
    </select>
  </div>

  <div class="mb-4">
    <label class="block text-gray-700 text-sm font-bold mb-2">
      File Name
    </label>
    <input onChange="fileHelpers.changeValue(this.value, 'file_name')" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="file_name" type="text" placeholder="sample.txt">
  </div>

  <div id="addContent">
    <div class="mb-4"></div>
  </div>

  <div class="flex items-center justify-between">
    <button onClick="fileHelpers.submitClick(this)" class="m-auto align-middle bg-blue-800 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline color" type="button">
      Set
    </button>
  </div>

  </form>
  `;
};

