const workout_json_to_last_pace = (workout_json) => {
  for (let i = workout_json.length - 1; i > -1; i--) {
    let current_set = workout_json[i];

    for (let j = current_set["lines"].length - 1; j > -1; j--) {
      current_line = current_set["lines"][j];

      if (current_line["distance"] !== 0) {
        return Math.round((time_string_to_seconds(current_line["interval"]) * 1.0) / (current_line["distance"] * 1.0) * 100.0);
      }
    }
  }
}
