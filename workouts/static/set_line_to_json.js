const set_regex_list = [
  /^(\d+)\s*(x|\u{00D7})\s*(\d+(?:\.\d+)?)\s*@\s*(\d\d:\d\d|\d:\d\d|:\d\d|\d\d|\d)\s*(.*)$/, // full set line
  /^(\d+(?:\.\d+)?)\s*@\s*(\d\d:\d\d|\d:\d\d|:\d\d|\d\d|\d)\s*(.*)$/, // no repeat set line
  /^(\d\d:\d\d|\d:\d\d|:\d\d|\d\d|\d)\s*(.*)$/ // rest line
];

const set_line_to_json = (set_line) => {
  index = 0;
  for (; index < set_regex_list.length; index++) {
    re = set_regex_list[index];
    if (re.test(set_line)) {
      break;
    }
  }

  if (index >= set_regex_list.length) {
    return null;
  }

  let regex_result = set_regex_list[index].exec(set_line);

  switch (index) {
    case 0:
      return {
        "repeats": parseInt(regex_result[1], 10),
        "distance": parseInt(regex_result[3], 10),
        "interval": regex_result[4],
        "description": regex_result[5],
        "notes": []
      };
    case 1:
      return {
        "repeats": 1,
        "distance": parseInt(regex_result[1], 10),
        "interval": regex_result[2],
        "description": regex_result[3],
        "notes": []
      };
    case 2:
      return {
        "repeats": 1,
        "distance": 0,
        "interval": regex_result[1],
        "description": regex_result[2],
        "notes": []
      }
    default:
      return null;
  }
};
