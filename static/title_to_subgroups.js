const title_to_subgroups = (title) => {
  const regex = /#(\w+)/g;
  const matches = title.match(regex);

  if (matches) {
    return matches.map(subgroup => subgroup.substring(1));
  } else {
    return [];
  }
};
