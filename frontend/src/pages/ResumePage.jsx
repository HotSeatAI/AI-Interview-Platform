import ResumeUploadCard from '../components/resume/ResumeUploadCard.jsx'
import AnalysisHistoryList from '../components/resume-analysis/AnalysisHistoryList.jsx'
import Navbar from '../components/layout/Navbar.jsx'
import PageHeader from '../components/layout/PageHeader.jsx'

function ResumePage() {
  return (
    <div className="resume-page">
      <Navbar />

      <PageHeader
        eyebrow="YOUR RESUME"
        title="This is what grounds your interview"
        subtitle="Every question HotSeat generates is built from the resume you upload here."
      />

      <main className="resume-container">
        <ResumeUploadCard />

        <section className="resume-section">
          <div className="section-header">
            <div className="eyebrow">PAST ANALYSES</div>
            <h2>Resume ↔ JD history</h2>
          </div>
          <AnalysisHistoryList />
        </section>
      </main>
    </div>
  )
}

export default ResumePage
