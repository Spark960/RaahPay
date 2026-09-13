import { BrowserRouter, Routes, Route } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import BorrowerDetail from "./pages/BorrowerDetail"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/borrower/:id" element={<BorrowerDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
