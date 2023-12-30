const time_regex_list = [
  /^(\d\d):(\d\d)$/,
  /^(\d):(\d\d)$/,
  /^:(\d\d)$/,
  /^(\d\d)$/,
  /^(\d)$/
];

const time_string_to_seconds = (time_string) => {
  index = 0;
  for (; index < time_regex_list.length; index++) {
    re = time_regex_list[index];
    if (re.test(time_string)) {
      break;
    }
  }

  let regex_result = time_regex_list[index].exec(time_string);

  switch (index) {
    case 0:
    case 1:
      return parseInt(regex_result[1], 10) * 60 + parseInt(regex_result[2], 10);
    case 2:
    case 3:
      return parseInt(regex_result[1], 10);
    case 4:
      return parseInt(regex_result[1], 10) * 60;
    default:
      alert("Failed Translation from Time String to Seconds. Bad Input.");
      return 0;
  }
};
