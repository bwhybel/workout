const blank_set_json = (subgroups = []) => {
    return {
	"lines": [],
	"rounds": 1,
	"title": "",
	"notes": [],
	"subgroups": subgroups,
	"pre_set_rest": 0
    };
}

const workout_text_to_json = (text, rest_seconds) => {
    array = text.split('\n');

    sets = [];
    current_set = blank_set_json();

    current_subgroups = [];
    array.forEach((line) => {
	rounds = round_line_to_rounds(line)
	set_json = set_line_to_json(line)
	note_json = note_line_to_json(line)

	if (rounds) {
	    current_set["rounds"] = rounds;
	} else if (set_json) {
	    current_set["lines"].push(set_json);
	} else if (note_json) {
	    switch (note_json["type"]) {
	    case "set_note":
		num_lines = current_set["lines"].length
		if (num_lines === 0) {
		    current_set["notes"].push(note_json["note"]);
		} else {
		    current_set["lines"][num_lines - 1]["notes"].push(note_json["note"]);
		}
		break;
	    case "set_title":
		current_set["title"] = note_json["note"];
		current_subgroups = note_json["subgroups"];
		current_set["subgroups"] = current_subgroups;
		current_set["pre_set_rest"] = rest_seconds;
		break;
	    }
	} else if (line.trim().length === 0) {
	    sets.push(current_set);
	    current_set = blank_set_json(current_subgroups);
	}
    });

    sets.push(current_set);

    return sets;
}
