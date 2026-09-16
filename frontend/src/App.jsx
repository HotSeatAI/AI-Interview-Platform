import { Suspense, useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { ResumeAnalysisProvider } from './context/ResumeAnalysisContext'
import HelpButton from './components/layout/HelpButton'
import LoginPromptModal from './components/auth/LoginPromptModal'
import useAuth from './hooks/useAuth'
import { setUnauthorizedHandler } from './api/client'

const LIVE_INTERVIEW_PATH = /^\/interview\/[^/]+$/

function App() {
  const location = useLocation()
  const showHelpButton = !LIVE_INTERVIEW_PATH.test(location.pathname)
  const { showLoginPrompt, promptLogin, dismissLoginPrompt } = useAuth()

  useEffect(() => {
    setUnauthorizedHandler(promptLogin)
  }, [promptLogin])

  return (
    <ResumeAnalysisProvider>
      <Suspense fallback={<div className="app-loading">Loading&hellip;</div>}>
        <Outlet />
      </Suspense>
      {showHelpButton && <HelpButton />}
      {showLoginPrompt && <LoginPromptModal onDismiss={dismissLoginPrompt} />}
    </ResumeAnalysisProvider>
  )
}

export default App
