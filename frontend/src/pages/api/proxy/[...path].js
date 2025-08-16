import axios from "axios";

export default async function handler(req, res) {
  const path = req.query.path.join("/");
  const base = "http://localhost:8000"; // FastAPI server
  const url = `${base}/${path}`;
  try {
    const apiRes = await axios({
      method: req.method,
      url,
      data: req.body,
      headers: { "Content-Type": "application/json" },
    });
    res.status(apiRes.status).json(apiRes.data);
  } catch (err) {
    res.status(err.response?.status || 500).json({ message: err.message });
  }
}
