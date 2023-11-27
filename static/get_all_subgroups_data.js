const get_all_subgroups_data = (workout_json) => {
    let subgroup_data = {};

    let all_subgroups_set = new Set();
    workout_json.forEach((set) => {
	set["subgroups"].forEach((subgroup) => {
	    all_subgroups_set.add(subgroup);
	});
    });

    if (all_subgroups_set.size === 0) {
	all_subgroups_set.add("all");
    }

    let all_subgroups = [...all_subgroups_set];
    workout_json.forEach((set) => {

	let set_distance = 0;
	let set_interval = 0;
	set["lines"].forEach((line) => {
	    set_distance += line["distance"] * line["repeats"] * set["rounds"];
	    set_interval += time_string_to_seconds(line["interval"]) * line["repeats"] * set["rounds"];
	});

	let set_interval_with_rest = set_interval + set["pre_set_rest"];

	current_subgroups = set["subgroups"];
	if (current_subgroups.length === 0) {
	    all_subgroups.forEach((subgroup) => {
		if (subgroup_data[subgroup]) {
		    subgroup_data[subgroup]["total_distance"] += set_distance;
		    subgroup_data[subgroup]["total_time"] += set_interval;
		    subgroup_data[subgroup]["total_time_with_rest"] += set_interval_with_rest;
		} else {
		    subgroup_data[subgroup] = {
			"total_distance": set_distance,
			"total_time": set_interval,
			"total_time_with_rest": set_interval_with_rest
		    }
		}
	    });
	} else {
	    current_subgroups.forEach((subgroup) => {
		if (subgroup_data[subgroup]) {
		    subgroup_data[subgroup]["total_distance"] += set_distance;
		    subgroup_data[subgroup]["total_time"] += set_interval;
		    subgroup_data[subgroup]["total_time_with_rest"] += set_interval_with_rest;
		} else {
		    subgroup_data[subgroup] = {
			"total_distance": set_distance,
			"total_time": set_interval,
			"total_time_with_rest": set_interval_with_rest
		    }
		}
	    });
	}

    });

    return subgroup_data;
};
