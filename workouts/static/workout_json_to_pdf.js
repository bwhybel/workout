const workout_json_to_pdf = (workout_json, workout_metadata, subgroups_data, image, logo_width) => {
  const {
    jsPDF
  } = window.jspdf;

  let pdf = new jsPDF({
    unit: 'px'
  });

  subgroups_list = Object.keys(subgroups_data);
  console.log(workout_json);
  console.log(subgroups_list);

  subgroups_list.forEach((subgroup) => {
    pdf.addImage(image, 'jpeg', (426.5 - logo_width), 15, logo_width, 85);
    pdf.setFont("Courier", "normal");
    pdf.setFontSize(20);
    pdf.text(workout_metadata["team"] + " " + workout_metadata["group"] + " (" + subgroup + ")", 20, 25);
    pdf.setFontSize(16);
    pdf.setFont("Courier", "italic");
    pdf.text(workout_metadata["date"] + " " + workout_metadata["time_of_day"], 20, 38);
    pdf.setFont("Courier", "bold");
    pdf.text(workout_metadata["title"], 20, 50);
    pdf.setFontSize(15);

    let pointer = 66;
    let left_margin = 20;

    workout_json.forEach((set) => {
      if (set["subgroups"].length === 0 || set["subgroups"].includes(subgroup)) {
        if (set["title"] !== "") {
          pdf.setFont("Courier", "bold");
          pdf.text(set["title"], left_margin, pointer);
          pdf.setFont("Courier", "normal");
          pointer += 11;
        }

        if (set["notes"].length !== 0) {
          pdf.setFontSize(13);
          pdf.setFont("Courier", "italic");
          set["notes"].forEach((note) => {
            pointer -= 1;
            pdf.text('\u2022 ' + note, left_margin + 5, pointer);
            pointer += 11;
          });
          pdf.setFontSize(15);
          pdf.setFont("Courier", "normal");
        }

        if (set["rounds"] !== 1) {
          pdf.text(set["rounds"] + " x {", left_margin, pointer);
          left_margin = 30;
          pointer += 11;
        }

        set["lines"].forEach((line) => {
          text = line_json_to_text(line)
          pdf.text(text, left_margin, pointer);
          pointer += 11;

          pdf.setFontSize(13);
          pdf.setFont("Courier", "italic");
          line["notes"].forEach((note) => {
            pointer -= 1;
            pdf.text('\u2022 ' + note, left_margin + 5, pointer);
            pointer += 11;
          });
          pdf.setFontSize(15);
          pdf.setFont("Courier", "normal");
        });

        left_margin = 20;
        pointer += 5;
      }
    });

    pdf.addPage();
  });

  // delete last page, because we always add a page each subgroup loop
  pdf.deletePage(pdf.internal.getNumberOfPages());
  pdf.save(workout_metadata["date"] + "_" +
    workout_metadata["time_of_day"] + "_" +
    workout_metadata["team"] + "_" +
    workout_metadata["group"] + ".pdf");
};
