function refreshAt(hours, minutes, seconds) {
    var now = new Date();
    var then = new Date();

    if(now.getHours() > hours ||
       (now.getHours() == hours && now.getMinutes() > minutes) ||
        now.getHours() == hours && now.getMinutes() == minutes && now.getSeconds() >= seconds) {
        then.setDate(now.getDate() + 1);
    }
    then.setHours(hours);
    then.setMinutes(minutes);
    then.setSeconds(seconds);

    var timeout = (then.getTime() - now.getTime());
    if (timeout > 0 && timeout < 3.6e+6) {
		setTimeout(function() { window.location.reload(true); }, timeout);
	}
}

var now = new Date();
var targetTime = new Date();
setTimeout(function() { window.location.reload(true); }, 60000)
if(now.getMinutes() > 10 && now.getMinutes() < 40) {
	targetTime.setMinutes(40);
} else {
	targetTime.setMinutes(10);
}
refreshAt(targetTime.getHours(),targetTime.getMinutes(),0);
