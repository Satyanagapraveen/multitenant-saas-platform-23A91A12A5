import Navbar from "../components/Navbar";

function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main className="p-6">{children}</main>
    </div>
  );
}

export default AppLayout;
