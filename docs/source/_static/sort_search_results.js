const getSearchTerm = () => {
  let search_outer_input = document.querySelector(".search__outer__input");
  if (search_outer_input !== null) {
      let word = search_outer_input.value
      if (/^[A-Z]/.test(word)) {  /* if first letter is capital, assume user is searching for a class */
          return "telegram." + word || "";  /* it could also be from ext, but this works well enough */
      }
      return search_outer_input.value || "";
  }
  return "";
}