const note_regex_list = [
    /--\s*(.+)\s*$/,
    /\/\/\s*(.+)\s*$/
];

const note_line_to_json = (note_line) => {
    index = 0;
    for( ; index < note_regex_list.length ; index++) {
	re = note_regex_list[index];
	if (re.test(note_line)) {
	    break;
	}
    }

    if (index >= note_regex_list.length) {
	return null;
    }

    let regex_result = note_regex_list[index].exec(note_line);

    note_json = {};

    switch(index) {
    case 0:
	note_json["type"] = "set_note";
	note_json["note"] = regex_result[1].trim();
	break;
    case 1:
	note_json["type"] = "set_title";
	note_json["note"] = title_without_subgroups(regex_result[1].trim());
	note_json["subgroups"] = title_to_subgroups(regex_result[1].trim());
	break;
    };

    return note_json;
};
