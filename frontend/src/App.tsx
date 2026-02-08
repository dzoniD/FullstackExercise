import { Routes, Route } from "react-router-dom";
import { Link } from "react-router-dom";
import SignIn from "./routes/signup/SignIn";
import Login from "./routes/login/Login";
import VerifyEmail from "./routes/VerifyEmail";
import TasksPage from "./routes/TasksPage/Tasks";

import { useNavigate } from "react-router-dom";
import "./App.css";
import ProtectedRoute from "./routes/ProtectedRoute";



function App() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };
  
  return (
    <>
      <div className="flex justify-end">
          <Link to="/signin" className="text-blue-500 hover:text-blue-600">Sign in</Link>
          <Link to="/login" className="text-blue-500 hover:text-blue-600">Log in</Link>
          <button onClick={handleLogout} className="text-blue-500 hover:text-blue-600">Logout</button>
      </div>
      <Routes>
      <Route path="/" element={<TasksPage />} />
      <Route path="/tasks" element={
        <ProtectedRoute>
            <TasksPage />
        </ProtectedRoute>
        } />
      <Route path="/signin" element={<SignIn />} />
      <Route path="/login" element={<Login />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      </Routes>
    </>
    
  );
}

export default App;
