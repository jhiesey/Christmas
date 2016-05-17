var express = require('express')
var fs = require('fs')
var http = require('http')
var jade = require('jade')
var path = require('path')
var url = require('url')

var DATA_PATH = path.join(__dirname, '../brightness.txt')
var TAIL_LENGTH = 100

function readBrightness (cb) {
  fs.readFile(DATA_PATH, {
    encoding: 'utf8'
  }, function (err, data) {
    if (err) {
      return cb(err)
    }
    var bright = parseFloat(data)
    cb(null, bright)
  })
}

function writeBrightness (bright, cb) {
  var contents = bright.toString()
  fs.writeFile(DATA_PATH, contents, cb)
}

var app = express()
var httpServer = http.createServer(app)

// Templating
app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'jade')
app.set('x-powered-by', false)
app.engine('jade', jade.renderFile)

app.use(express.static(path.join(__dirname, 'static')))

app.get('/', function (req, res, next) {
  readBrightness(function (err, bright) {
    if (err) {
      return next(err)
    }

    res.render('index', {
      title: 'Lights',
      bright: bright
    })
  })
})

app.post('/setbright', function (req, res, next) {
  console.log('GOT SETBRIGHT')
  var bright = req.query.bright
  if (bright === undefined) {
    return next(new Error('bright not specified'))
  }

  writeBrightness(bright, function (err) {
    if (err) {
      return next(err)
    }
    res.send('ok')
  })
})

app.get('*', function (req, res) {
  res.status(404).render('error', {
    title: '404 Page Not Found - lights',
    message: '404 Not Found'
  })
})

// error handling middleware
app.use(function (err, req, res, next) {
  error(err)
  res.status(500).render('error', {
    title: '500 Server Error - lights',
    message: err.message || err
  })
})

httpServer.listen(9000)

function error (err) {
  console.error(err.stack || err.message || err)
}
