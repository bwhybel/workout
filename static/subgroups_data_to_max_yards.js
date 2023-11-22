const subgroups_data_to_max_yards = (subgroups_data) => {
    max_yards = 0;
    Object.keys(subgroups_data).forEach((key) => {
	subgroup_data = subgroups_data[key];
	if (subgroup_data["total_distance"] > max_yards) {
	    max_yards = subgroup_data["total_distance"];
	}
    });
    return max_yards;
}
