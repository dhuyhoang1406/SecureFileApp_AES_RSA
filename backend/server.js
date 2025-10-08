import express from "express";
import dotenv from "dotenv";
import sequelize from "./config/connectDB.js";
import route from "./routes/index.js";
dotenv.config();

const app = express();
app.use(express.json());

// Kết nối database
(async () => {
  try {
    await sequelize.authenticate();
    console.log("✅ Database connected successfully!");
  } catch (error) {
    console.error("❌ Unable to connect to the database:", error);
  }
})();

// Mount routes
app.use("/api", route); 

app.get("/", (req, res) => {
  res.json({ message: "Server is running 🚀" });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
});
