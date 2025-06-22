// server.js or index.js
const express = require('express');
const app = express();
const PORT = 5000;
const cors = require('cors');
app.use(cors());

// Middleware to parse JSON
app.use(express.json());

// POST endpoint to receive difficulty
app.post('/api/difficulty', (req, res) => {
  const { difficulty } = req.body;

  // Validate the difficulty value
  const validDifficulties = ['Beginner', 'Intermediate', 'Advanced'];
  if (!validDifficulties.includes(difficulty)) {
    return res.status(400).json({ error: 'Invalid difficulty level' });
  }

  // Simulate saving it (to DB, memory, etc.)
  console.log(`Received difficulty: ${difficulty}`);

  // Send success response
  res.status(200).json({ success: true, updatedDifficulty: difficulty });
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
