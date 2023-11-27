const line_json_to_text = (line_json) => {
    return (line_json["repeats"] > 1 ? line_json["repeats"] + " x " : "") +
	(line_json["distance"] > 0 ? line_json["distance"] + " @ " : "") +
	line_json["interval"] +
	" " +
	line_json["description"];
}
