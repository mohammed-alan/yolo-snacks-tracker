import { useEffect, useState } from "react";
import { io } from "socket.io-client";

function App() {
  const [detections, setDetections] = useState([]);
  const [frame, setFrame] = useState(null);
  const [status, setStatus] = useState("Disconnected");

  // Calories lookup table
  const caloriesMap = {
    reeses: 110,
    aero: 50,
    snickers: 80,
    twix: 80,
    kitkat: 70,
  };

  const normalizeClass = (name) =>
  name.toLowerCase().replace(/['\s]/g, "");

  useEffect(() => {
    const socket = io("http://localhost:8000", {
      transports: ["polling"], // fallback for Eventlet
    });

    socket.on("connect", () => {
      console.log("Connected to backend:", socket.id);
      setStatus("Connected");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from backend");
      setStatus("Disconnected");
    });

    socket.on("detections", (data) => {
      if (data?.frame) setFrame(`data:image/jpeg;base64,${data.frame}`);
      if (data?.detections) {
        setDetections((prev) => {
          const prevStr = JSON.stringify(prev);
          const newStr = JSON.stringify(data.detections);
          return prevStr !== newStr ? data.detections : prev;
        });
      }
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center p-6">
  <h1 className="text-4xl font-extrabold mb-2 text-amber-400">
    Live YOLO Detections
  </h1>
  <p
    className={`mb-6 ${
      status === "Connected" ? "text-green-400" : "text-red-400"
    }`}
  >
    {status}
  </p>

  {/* Layout: Feed + Detections side by side */}
  <div className="w-full max-w-6xl flex flex-col lg:flex-row gap-6">
    {/* Live Feed */}
    <div className="flex-1 rounded-xl overflow-hidden shadow-2xl border-4 border-amber-500">
      {frame ? (
        <img
          src={frame}
          alt="Live Feed"
          className="w-full h-auto object-contain"
        />
      ) : (
        <div className="w-full h-80 flex items-center justify-center bg-gray-800 text-gray-400">
          Waiting for camera feed...
        </div>
      )}
    </div>

    {/* Detections Table */}
    <div className="w-full lg:w-2/5 bg-gray-900 rounded-xl shadow-2xl p-6 max-h-[500px] overflow-y-auto">
      <h2 className="text-2xl font-semibold mb-4 text-amber-300">
        Detected Chocolates
      </h2>

      {detections.length > 0 ? (
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="bg-gray-800 text-left">
              <th className="py-3 px-4 text-amber-400 uppercase tracking-wide">
                Chocolate Type
              </th>
              <th className="py-3 px-4 text-amber-400 uppercase tracking-wide">
                Confidence
              </th>
              <th className="py-3 px-4 text-amber-400 uppercase tracking-wide">
                Calories
              </th>
            </tr>
          </thead>
          <tbody>
            {detections.map((det, idx) => (
              <tr
                key={idx}
                className={`border-b border-gray-700 ${
                  idx % 2 === 0 ? "bg-gray-900" : "bg-gray-950"
                } hover:bg-gray-800 transition-colors duration-200`}
              >
                <td className="py-2 px-4">{det.class}</td>
                <td className="py-2 px-4">
                  {(det.confidence * 100).toFixed(1)}%
                </td>
                <td className="py-2 px-4">
                  {caloriesMap[normalizeClass(det.class)] ?? "N/A"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-gray-500 text-center py-4">
          No detections yet...
        </p>
      )}
    </div>
  </div>
</div>

  );
}

export default App;
