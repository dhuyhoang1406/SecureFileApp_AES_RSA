// server.js
import express from "express";
import dotenv from "dotenv";
import sequelize from "./config/connectDB.js";
import route from "./routes/index.js";
import morgan from "morgan"; // THÊM: LOG REQUEST

dotenv.config();

const app = express();

// THÊM: LOG TẤT CẢ REQUEST (GET, POST, lỗi,...)
app.use(morgan("combined")); // hoặc "dev" để đẹp hơn

app.use(express.json({ limit: "10mb" })); // TĂNG LIMIT (key PEM dài)

// Kết nối database
(async () => {
  try {
    await sequelize.authenticate();
    console.log("Database connected successfully!");
  } catch (error) {
    console.error("Unable to connect to the database:", error);
  }
})();

// Mount routes
app.use("/api", route);

// THÊM: ERROR HANDLING MIDDLEWARE (BẮT TẤT CẢ LỖI)
app.use((err, req, res, next) => {
  console.error("UNHANDLED ERROR:", err.stack); // IN CHI TIẾT LỖI
  res.status(500).json({
    error: 1,
    message: "Internal Server Error",
    details: process.env.NODE_ENV === "development" ? err.message : undefined
  });
});

// Trang chủ
app.get("/", (req, res) => {
  res.json({ message: "Server is running" });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});