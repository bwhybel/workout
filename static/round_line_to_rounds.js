const round_regex_list = [
  /(\d+)\s*(x|X|×)\s*{\s*$/, // rounds with x
  /(\d+)\s*rounds\s*$/, // rounds with language
];

const round_line_to_rounds = (round_line) => {
  index = 0;
  for (; index < round_regex_list.length; index++) {
    re = round_regex_list[index];
    if (re.test(round_line)) {
      break;
    }
  }

  if (index >= round_regex_list.length) {
    return null;
  }

  regex_result_list = round_regex_list[index].exec(round_line);

  return regex_result_list[1];
};
