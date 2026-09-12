import { Outlet, useLocation } from 'react-router-dom'
import { ResumeAnalysisProvider } from './context/ResumeAnalysisContext'
import HelpButton from './components/layout/HelpButton'

const LIVE_INTERVIEW_PATH = /^\/interview\/[^/]+$/

function App() {
  const location = useLocation()
  const showHelpButton = !LIVE_INTERVIEW_PATH.test(location.pathname)

  return (
    <ResumeAnalysisProvider>
      <Outlet />
      {showHelpButton && <HelpButton />}
    </ResumeAnalysisProvider>
  )
}

export default App
