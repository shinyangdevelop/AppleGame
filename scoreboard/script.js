document.addEventListener("DOMContentLoaded", () => {
  const scoreboard = document.getElementById("scoreboard");

  fetch("list.json")
    .then((response) => response.json())
    .then((data) => {
      // Sort data by score in descending order
      data.sort((a, b) => b.score - a.score);

      // Populate the scoreboard
      data.forEach((user) => {
        const entry = document.createElement("div");
        entry.classList.add("score-entry");

        const nameEl = document.createElement("span");
        nameEl.classList.add("name");
        nameEl.textContent = user.name;

        const scoreEl = document.createElement("span");
        scoreEl.classList.add("score");
        scoreEl.textContent = (user.score > 0 ? "+" : "") + user.score;

        entry.appendChild(nameEl);
        entry.appendChild(scoreEl);

        scoreboard.appendChild(entry);
      });
    })
    .catch((error) => {
      console.error("Error fetching scoreboard data:", error);
      scoreboard.textContent = "Failed to load scoreboard.";
    });
});
