var slider = document.querySelector('input')

slider.addEventListener('input', function () {
	trigger()
})

var DEBOUNCE_DELAY = 0.25 // seconds

var triggerTimer = null
function trigger () {
	if (triggerTimer) {
		clearTimeout(triggerTimer)
	}

	triggerTimer = setTimeout(setBrightness, DEBOUNCE_DELAY * 1000)
}

function setBrightness () {
	var bright = slider.value / 100
	var xhr = new XMLHttpRequest()
	var url = '/setbright?bright=' + bright
	xhr.open('POST', url)
	xhr.send()
}