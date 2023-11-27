const title_without_subgroups = (title) => {
  const hashTagsRegex = /#\w+\b/g;
  const hashTags = title.match(hashTagsRegex) || [];

  hashTags.forEach(tag => {
    title = title.replace(tag, '');
  });

  return title.trim();
}
