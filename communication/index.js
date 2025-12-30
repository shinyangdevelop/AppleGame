const express = require("express");
const { nanoid } = require("nanoid");
const bodyParser = require("body-parser");

const app = express();
const port = 3000;

// In-memory store for data
const dataStore = {};

app.use(bodyParser.json()); // To parse JSON request bodies

// POST endpoint to store 2D array data
app.post("/data", (req, res) => {
  const { data } = req.body; // Expecting data to be a string representing a 2D array

  if (typeof data !== "string") {
    return res.status(400).json({ error: "Data must be a string." });
  }

  const key = nanoid(10); // Generate a 10-character unique key
  dataStore[key] = data;

  res.status(201).json({ key });
});

// GET endpoint to retrieve 2D array data
app.get("/data/:key", (req, res) => {
  const { key } = req.params;
  const data = dataStore[key];

  if (data) {
    res.status(200).json({ data });
  } else {
    res.status(404).json({ error: "Data not found for the given key." });
  }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
