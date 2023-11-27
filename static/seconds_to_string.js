const seconds_to_string = (num_seconds, short_format = false) => {
    if (!num_seconds) {
	return short_format ? "0:00" : "00:00:00";
    }
    let hours = Math.floor(num_seconds / 3600);
    num_seconds -= hours * 3600;
    let minutes = Math.floor(num_seconds / 60);
    num_seconds -= minutes * 60;
    let seconds = short_format ? Math.round(num_seconds * 10.0) / 10.0 : num_seconds;
    return short_format ? minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0') : hours.toString().padStart(2, '0') + ":" + minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
};
