import HistoryList from "../components/history/HistoryList";
import Navbar from "../components/layout/Navbar.jsx";
import PageHeader from "../components/layout/PageHeader.jsx";

function HistoryPage() {
  return (
    <div className="history-page">
      <Navbar />
      <PageHeader
        eyebrow="HISTORY"
        title="Interview history"
        subtitle="Review previous sessions and continue anything unfinished."
      />
      <main className="history-container">
        <HistoryList />
      </main>
    </div>
  );
}

export default HistoryPage;
