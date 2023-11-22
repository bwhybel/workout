const workout_json_to_seconds = (workout_json, workout_metadata, subgroups_data) => {
    let seconds = {};
    seconds._type = "pack";
    seconds.name = "Shared Timers";
    seconds.items = [];

    let folder = {};
    folder._type = "pack";
    folder.name = workout_metadata["team"] + " " +
	workout_metadata["group"] + " " +
	workout_metadata["date"] + " " +
	workout_metadata["time_of_day"];
    folder.color = 3;
    folder.items = [];

    subgroups_list = Object.keys(subgroups_data);
    subgroups_list.forEach((subgroup) => {
	let whole_workout = {};
	whole_workout.overrun = false;

        whole_workout._type = "cust";
        whole_workout.type = 0;
        whole_workout.name = subgroup;
        whole_workout.soundScheme = 1;
        whole_workout.activity = 46;
        whole_workout.intervals = [];

	workout_json.forEach((set) => {
	    if (set["subgroups"].length === 0 || set["subgroups"].includes(subgroup)) {
		if (set["pre_set_rest"] > 0) {
		    let rest_line = {};
                    rest_line.splitRest = 0;
                    rest_line.ducked = false;
                    rest_line.rest = false;
                    rest_line.color = Math.floor(Math.random() * 9) + 1;
                    rest_line.indefinite = false;
                    rest_line.split = false;
                    rest_line.vibration = false;
                    rest_line.halfwayAlert = false;
                    rest_line.duration = set["pre_set_rest"];
                    rest_line._type = "int";
                    rest_line.name = "Rest, Setting up Next Set";
                    whole_workout.intervals.push(rest_line);
		}

		for (let i = 0; i < set["rounds"]; i++) {
		    set["lines"].forEach((line) => {
			color = Math.floor(Math.random() * 9) + 1;
			for (let j = 0; j < line["repeats"]; j++) {
			    let workouts_line = {};
                            workouts_line.splitRest = 0;
                            workouts_line.ducked = false;
                            workouts_line.rest = false;
                            workouts_line.color = color;
                            workouts_line.indefinite = false;
                            workouts_line.split = false;
                            workouts_line.vibration = false;
                            workouts_line.halfwayAlert = false;
                            workouts_line.duration = time_string_to_seconds(line["interval"]);
                            workouts_line._type = "int";
                            name_distance = (line["distance"] > 0 ? line["distance"] + " " : "");
                            name_set_num = (line["repeats"] == 1 ? "" : " (" + (j + 1) + "/" + line["repeats"] + ")");
                            name_round_num = (set["rounds"] == 1 ? "" : " [" + (i + 1) + "/" + set["rounds"] + "]");
                            workouts_line.name = name_distance + line["description"] + name_set_num + name_round_num;
                            whole_workout.intervals.push(workouts_line);
			}
		    });
		}
	    }
	});
	folder.items.push(whole_workout);
    });

    seconds.items.push(folder);

    return seconds;
}
