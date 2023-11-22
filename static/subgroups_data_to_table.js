const subgroups_data_to_table = (subgroups_data) => {
    const table = document.createElement("table");

    const headerRow = table.insertRow();
    [
	"Subgroup",
	"Total Yards",
	"Total Time",
	"Total Time w/ Rest"
    ].forEach((header_title) => {
	const headerCell = headerRow.insertCell();
	headerCell.textContent = header_title;
    });

    Object.keys(subgroups_data).forEach((key) => {
	subgroup_data = subgroups_data[key];
	const row = table.insertRow();
	const subgroup_name = row.insertCell();
	subgroup_name.textContent = key;
	const total_yards = row.insertCell();
	total_yards.textContent = subgroup_data["total_distance"];
	const total_time = row.insertCell();
	total_time.textContent = seconds_to_string(subgroup_data["total_time"]);
	const total_time_with_rest = row.insertCell();
	total_time_with_rest.textContent = seconds_to_string(subgroup_data["total_time_with_rest"]);
    });

    return table;
}
