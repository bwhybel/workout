const set_regex_list = [
    /(\d+)\s*(x|X|\u{00D7})\s*{$/, // rounds with x
    /(\d+)\s*rounds\s*$/, // rounds with language
];

const round_line_to_rounds = (round_line) => {
    index = 0;
    for( ; index < set_regex_list.length ; index++) {
	re = set_regex_list[index];
	if (re.test(set_line)) {
	    break;
	}
    }

    if (index >= set_regex_list.length) {
	return null;
    }

    regex_result_list = set_regex_list[index].exec(round_line);

    return regex_result_list[1];
};
