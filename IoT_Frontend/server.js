var express = require('express');
var app = express();

//setting middleware
app.use(express.static(__dirname + '/public'));   //Serves resources from public folder

app.post('/gpioOperation', (req, res) => {
  res.send('Set up Pin Succeed !');
});

app.post('/timerOperation', (req, res) => {
  res.send('PWM has started !');
});

app.post('/uartOperation', (req, res) => {
  res.send('UART has started !, data received: [0x00, 0x00]');
});

app.post('/i2cOperation', (req, res) => {
  res.send('i2c has started !, data received: [0x01, 0x02]');
});

app.post('/spiOperation', (req, res) => {
  res.send('spi has started !, data received: [0x03, 0x04]');
});

app.post('/adcOperation', (req, res) => {
  res.send('ADC has started ! value: 0x47');
});

app.post('/schedulerOperation', (req, res) => {
  res.send('scheduler has started !');
});

app.post('/filesystemOperation', (req, res) => {
  res.send('file system operation completes !');
});

app.post('/firmwareupgradeOperation', (req, res) => {
  res.send('Firmware upgrade completed !');
});

var server = app.listen(5000);