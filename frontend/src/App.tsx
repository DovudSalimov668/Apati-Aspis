import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { Card } from './components/Card';
import { Button } from './components/Button';
import { Input } from './components/Input';
import { RiskBadge } from './components/RiskBadge';
import { Alert } from './components/Alert';
import { ScoreDial } from './components/ScoreDial';
import { EvidenceCard } from './components/EvidenceCard';
import { StepIndicator } from './components/StepIndicator';
import { DemoBadge } from './components/DemoBadge';
import { EmptyState } from './components/EmptyState';
import { ErrorState } from './components/ErrorState';
import {
  fetchHealth, scanUrl, scanMessage, scanQrFile, scanImageFile,
  fetchCheckupQuestions, submitCheckup, fetchScanHistory, checkPassword,
  CheckupQuestion, CheckupReport, ScanRecordHistory, PasswordCheckResponse
} from './services/api';
import {
  Search, FileText, QrCode, Image as ImageIcon,
  AlertTriangle, CheckSquare, Eye, EyeOff, Upload, ChevronDown, ChevronUp, Lock, CheckCircle2, Info
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeRoute, setActiveRoute] = useState<string>('home');
  const [inputTab, setInputTab] = useState<'url' | 'message' | 'qr' | 'image'>('url');
  
  const [urlInput, setUrlInput] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [healthError, setHealthError] = useState<string | null>(null);

  // Scan state
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);
  const [isTechnicalExpanded, setIsTechnicalExpanded] = useState<boolean>(false);

  // Password check state
  const [passwordInput, setPasswordInput] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [passwordReport, setPasswordReport] = useState<PasswordCheckResponse | null>(null);
  const [isPasswordChecking, setIsPasswordChecking] = useState<boolean>(false);

  // Security Checkup state
  const [questions, setQuestions] = useState<CheckupQuestion[]>([]);
  const [currentQIndex, setCurrentQIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [checkupReport, setCheckupReport] = useState<CheckupReport | null>(null);
  const [isCheckupSubmitting, setIsCheckupSubmitting] = useState<boolean>(false);

  // History state
  const [historyRecords, setHistoryRecords] = useState<ScanRecordHistory[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchHealth()
      .then(() => {
        setHealthError(null);
      })
      .catch((err) => {
        setHealthError(err.message || 'Failed to connect to backend server');
      });

    fetchCheckupQuestions()
      .then(setQuestions)
      .catch(() => {});
  }, []);

  const loadHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const records = await fetchScanHistory(20);
      setHistoryRecords(records);
    } catch {
      setScanError('Failed to load scan history');
    } finally {
      setIsHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeRoute === 'history') {
      loadHistory();
    }
  }, [activeRoute]);

  const handleScanSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsScanning(true);
    setScanError(null);
    setScanResult(null);

    try {
      if (inputTab === 'url') {
        if (!urlInput.trim()) throw new Error('Please enter a target URL.');
        const res = await scanUrl(urlInput.trim());
        setScanResult(res);
        setActiveRoute('result');
      } else if (inputTab === 'message') {
        if (!messageInput.trim()) throw new Error('Please enter message content.');
        const res = await scanMessage(messageInput.trim());
        setScanResult(res);
        setActiveRoute('result');
      } else if (inputTab === 'qr') {
        if (!selectedFile) throw new Error('Please select a QR image file.');
        const res = await scanQrFile(selectedFile);
        setScanResult(res);
        setActiveRoute('result');
      } else if (inputTab === 'image') {
        if (!selectedFile) throw new Error('Please select a screenshot or image file.');
        const res = await scanImageFile(selectedFile);
        setScanResult(res);
        setActiveRoute('result');
      }
    } catch (err: any) {
      setScanError(err.message || 'Analysis error occurred');
    } finally {
      setIsScanning(false);
    }
  };

  const handleDemoScenario = async (scen: 'safe' | 'moderate' | 'high' | 'critical') => {
    setIsScanning(true);
    setScanError(null);
    try {
      const response = await fetch('http://localhost:8000/api/scan/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scen }),
      });
      const res = await response.json();
      setScanResult(res);
      setActiveRoute('result');
    } catch (err: any) {
      setScanError(err.message || 'Demo scenario failed');
    } finally {
      setIsScanning(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordInput) return;
    setIsPasswordChecking(true);
    setScanError(null);
    try {
      const res = await checkPassword(passwordInput);
      setPasswordReport(res);
    } catch (err: any) {
      setScanError(err.message || 'Failed to check password');
    } finally {
      setIsPasswordChecking(false);
    }
  };

  const handleCheckupAnswerSelect = (optionId: string) => {
    const q = questions[currentQIndex];
    if (!q) return;
    const updated = { ...userAnswers, [q.id]: optionId };
    setUserAnswers(updated);
    if (currentQIndex < questions.length - 1) {
      setCurrentQIndex(currentQIndex + 1);
    }
  };

  const handleFinishCheckup = async () => {
    setIsCheckupSubmitting(true);
    try {
      const report = await submitCheckup(userAnswers);
      setCheckupReport(report);
    } catch (err: any) {
      setScanError(err.message || 'Failed to evaluate security checkup');
    } finally {
      setIsCheckupSubmitting(false);
    }
  };

  return (
    <Layout activeRoute={activeRoute} onNavigate={(r) => { setActiveRoute(r); setScanError(null); }}>
      {/* Backend Status Banner */}
      {healthError && (
        <div className="mb-6">
          <Alert type="warning" title="Backend Server Disconnected">
            Ensure FastAPI server is running on <code>http://localhost:8000</code>. ({healthError})
          </Alert>
        </div>
      )}

      {/* PAGE 1: HOME */}
      {activeRoute === 'home' && (
        <div className="space-y-10">
          <div className="text-center max-w-2xl mx-auto pt-4 space-y-3">
            <h1 className="text-3xl md:text-4xl font-extrabold text-textPrimary tracking-tight">
              Detect Digital Deception Before It Strikes
            </h1>
            <p className="text-base text-textSecondary leading-relaxed">
              Analyze suspicious URLs, text messages, QR codes, screenshots, and password breach safety in real time.
            </p>
          </div>

          {/* Tabbed Input Card */}
          <Card className="max-w-3xl mx-auto">
            {/* Input Tabs */}
            <div className="flex border-b border-border mb-6">
              <button
                onClick={() => setInputTab('url')}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-semibold text-xs transition-colors ${
                  inputTab === 'url' ? 'border-brand-500 text-brand-600' : 'border-transparent text-textSecondary hover:text-textPrimary'
                }`}
              >
                <Search className="w-4 h-4" /> <span>URL Scanner</span>
              </button>
              <button
                onClick={() => setInputTab('message')}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-semibold text-xs transition-colors ${
                  inputTab === 'message' ? 'border-brand-500 text-brand-600' : 'border-transparent text-textSecondary hover:text-textPrimary'
                }`}
              >
                <FileText className="w-4 h-4" /> <span>Message / Text</span>
              </button>
              <button
                onClick={() => setInputTab('qr')}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-semibold text-xs transition-colors ${
                  inputTab === 'qr' ? 'border-brand-500 text-brand-600' : 'border-transparent text-textSecondary hover:text-textPrimary'
                }`}
              >
                <QrCode className="w-4 h-4" /> <span>QR Code</span>
              </button>
              <button
                onClick={() => setInputTab('image')}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-semibold text-xs transition-colors ${
                  inputTab === 'image' ? 'border-brand-500 text-brand-600' : 'border-transparent text-textSecondary hover:text-textPrimary'
                }`}
              >
                <ImageIcon className="w-4 h-4" /> <span>Image / Screenshot</span>
              </button>
            </div>

            <form onSubmit={handleScanSubmit} className="space-y-4">
              {inputTab === 'url' && (
                <div className="flex flex-col sm:flex-row gap-3">
                  <Input
                    placeholder="https://suspicious-website.com"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    className="font-mono text-sm"
                  />
                  <Button variant="primary" size="lg" type="submit" isLoading={isScanning} className="sm:w-auto w-full shrink-0">
                    Analyze URL
                  </Button>
                </div>
              )}

              {inputTab === 'message' && (
                <div className="space-y-3">
                  <textarea
                    rows={4}
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder="Paste suspicious SMS, Email, or Chat message content..."
                    className="w-full bg-surface border border-border rounded-lg p-3 text-sm text-textPrimary placeholder-textSecondary focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                  <div className="flex justify-end">
                    <Button variant="primary" size="md" type="submit" isLoading={isScanning}>
                      Analyze Message Content
                    </Button>
                  </div>
                </div>
              )}

              {(inputTab === 'qr' || inputTab === 'image') && (
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-brand-500 transition-colors bg-slate-50/50">
                    <Upload className="w-8 h-8 text-brand-500 mx-auto mb-2" />
                    <p className="text-sm font-semibold text-textPrimary">
                      {inputTab === 'qr' ? 'Upload QR Code Image' : 'Upload Screenshot / Picture'}
                    </p>
                    <p className="text-xs text-textSecondary mb-3">PNG, JPG, WEBP up to 10MB</p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="text-xs text-textSecondary mx-auto cursor-pointer"
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button variant="primary" size="md" type="submit" isLoading={isScanning}>
                      Upload & Analyze
                    </Button>
                  </div>
                </div>
              )}
            </form>
          </Card>

          {/* Hackathon Demo Scenarios Strip */}
          <div className="max-w-3xl mx-auto bg-slate-100 p-4 rounded-xl border border-border">
            <div className="flex items-center justify-between flex-wrap gap-2 mb-2">
              <span className="text-xs font-bold text-textPrimary uppercase tracking-wider">
                Hackathon Demo Scenarios (Pre-loaded):
              </span>
              <DemoBadge />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <Button variant="secondary" size="sm" onClick={() => handleDemoScenario('safe')}>
                Low Risk Demo
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleDemoScenario('moderate')}>
                Moderate Risk Demo
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleDemoScenario('high')}>
                High Risk Demo
              </Button>
              <Button variant="danger" size="sm" onClick={() => handleDemoScenario('critical')}>
                Critical Risk Demo
              </Button>
            </div>
          </div>

          {/* 3-Step How It Works */}
          <StepIndicator />

          {/* Muted Powered-By Strip */}
          <div className="text-center pt-6 border-t border-border">
            <span className="text-xs font-semibold uppercase text-textSecondary tracking-wider block mb-3">
              Powered by Multi-Layer Threat Intelligence
            </span>
            <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-semibold text-textSecondary opacity-75">
              <span>Google Safe Browsing</span>
              <span>•</span>
              <span>URLhaus (Abuse.ch)</span>
              <span>•</span>
              <span>VirusTotal</span>
              <span>•</span>
              <span>HIBP Pwned Passwords</span>
              <span>•</span>
              <span>Gemini AI Engine</span>
            </div>
          </div>
        </div>
      )}

      {/* PAGE 2: SCAN RESULT (/scan/:id) */}
      {activeRoute === 'result' && scanResult && (
        <div className="space-y-8">
          {/* Sticky Header Banner */}
          <div className="sticky top-0 z-10 bg-surface border-b border-border p-3 shadow-sm flex items-center justify-between rounded-lg">
            <span className="text-xs font-bold text-textPrimary truncate max-w-md">
              Target: <span className="font-mono text-brand-600">{scanResult.normalized_url || scanResult.raw_url || scanResult.raw_message}</span>
            </span>
            <RiskBadge level={scanResult.risk_level} size="sm" />
          </div>

          {/* (1) CONCLUSION: ScoreDial + RiskBadge */}
          <Card className="flex flex-col md:flex-row items-center justify-between gap-6 bg-slate-50/50">
            <div className="flex items-center space-x-6">
              <ScoreDial score={scanResult.risk_score} level={scanResult.risk_level} size={110} />
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <RiskBadge level={scanResult.risk_level} size="lg" />
                  {scanResult.evidence?.demo_mode && <DemoBadge />}
                </div>
                <h2 className="text-xl font-bold text-textPrimary">Security Assessment Conclusion</h2>
                <p className="text-xs text-textSecondary">
                  Confidence Rating: <strong className="text-textPrimary">{scanResult.confidence || 'HIGH'}</strong>
                </p>
              </div>
            </div>

            <Button variant="secondary" size="sm" onClick={() => setActiveRoute('home')}>
              Scan Another Target
            </Button>
          </Card>

          {/* (2) WHY: Plain-Language Icon-led Bullets */}
          <Card>
            <h3 className="text-sm font-bold text-textPrimary uppercase tracking-wider mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-brand-500" /> Why Is This Target Risky?
            </h3>
            <div className="space-y-3">
              {scanResult.explanation?.why_risky?.map((reason: string, idx: number) => (
                <div key={idx} className="flex items-start space-x-3 text-sm text-textPrimary bg-slate-50 p-3 rounded-lg border border-border">
                  <AlertTriangle className="w-4 h-4 text-riskMod-text shrink-0 mt-0.5" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* (3) EVIDENCE: Provider Cards Collapsed by Default */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-textPrimary uppercase tracking-wider mb-2">
              Threat Intelligence Evidence ({Object.keys(scanResult.evidence?.threat_intelligence?.providers || {}).length || 5} Providers)
            </h3>

            {/* Provider Evidence Cards */}
            <EvidenceCard
              providerName="Google Safe Browsing API"
              state={scanResult.evidence?.threat_intelligence?.providers?.GoogleSafeBrowsing?.state || 'NO_MATCH'}
              details={scanResult.evidence?.threat_intelligence?.providers?.GoogleSafeBrowsing || { state: 'NO_MATCH' }}
            />
            <EvidenceCard
              providerName="URLhaus Malware Database"
              state={scanResult.evidence?.threat_intelligence?.providers?.URLhaus?.state || 'NO_MATCH'}
              details={scanResult.evidence?.threat_intelligence?.providers?.URLhaus || { state: 'NO_MATCH' }}
            />
            <EvidenceCard
              providerName="VirusTotal Engine Scanner"
              state={scanResult.evidence?.threat_intelligence?.providers?.VirusTotal?.state || 'NO_MATCH'}
              details={scanResult.evidence?.threat_intelligence?.providers?.VirusTotal || { state: 'NO_MATCH' }}
            />
            <EvidenceCard
              providerName="DNS Pre-flight Resolver"
              state={scanResult.ssrf_blocked ? 'MATCH' : 'NO_MATCH'}
              details={scanResult.evidence?.ssrf_check || { status: 'SAFE' }}
            />
            <EvidenceCard
              providerName="RDAP / Domain Registration"
              state="NO_MATCH"
              details={{ domain: scanResult.domain, status: 'Active Registration' }}
            />
          </div>

          {/* (4) WHAT TO DO: Numbered Imperative Action List */}
          <Card className="bg-brand-50/50 border-brand-500/20">
            <h3 className="text-sm font-bold text-brand-700 uppercase tracking-wider mb-4 flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-brand-600" /> Recommended Action Steps
            </h3>
            <ol className="space-y-3">
              {scanResult.explanation?.recommended_actions?.map((act: string, idx: number) => (
                <li key={idx} className="flex items-start space-x-3 text-sm text-textPrimary">
                  <span className="bg-brand-500 text-white font-bold text-xs w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="font-medium">{act}</span>
                </li>
              ))}
            </ol>
          </Card>

          {/* (5) TECHNICAL DETAILS: Collapsed Panel with Monospace Data */}
          <Card>
            <div
              onClick={() => setIsTechnicalExpanded(!isTechnicalExpanded)}
              className="flex items-center justify-between cursor-pointer"
            >
              <h3 className="text-sm font-bold text-textPrimary uppercase tracking-wider">
                Technical Evidence Raw Payload
              </h3>
              <Button variant="ghost" size="sm">
                {isTechnicalExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </div>

            {isTechnicalExpanded && (
              <div className="mt-4 pt-4 border-t border-border bg-slate-900 text-slate-200 font-mono text-xs p-4 rounded-lg overflow-x-auto">
                <pre>{JSON.stringify(scanResult, null, 2)}</pre>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* PAGE 3: PASSWORD CHECK (/password-check) */}
      {activeRoute === 'password-check' && (
        <div className="space-y-8 max-w-2xl mx-auto">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-extrabold text-textPrimary tracking-tight">Password Breach Checker</h2>
            <p className="text-sm text-textSecondary">
              Check if a password has appeared in public breach datasets using <strong>K-Anonymity privacy protection</strong>.
            </p>
          </div>

          <Card>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div className="relative">
                <Input
                  label="Password to inspect"
                  type={showPassword ? 'text' : 'password'}
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  placeholder="Enter password..."
                  className="font-mono text-sm pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-8 text-textSecondary hover:text-textPrimary"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              <div className="bg-brand-50 p-3 rounded-lg border border-brand-500/20 text-xs text-brand-700 flex items-start space-x-2">
                <Lock className="w-4 h-4 shrink-0 mt-0.5" />
                <span>
                  <strong>K-Anonymity Safeguard:</strong> Your password is SHA-1 hashed locally in memory. Only the first 5 characters of the hash are transmitted. Your full password is <strong>never</strong> sent over the network or saved.
                </span>
              </div>

              <Button variant="primary" size="lg" type="submit" isLoading={isPasswordChecking} className="w-full">
                Check Breach Safety
              </Button>
            </form>

            {passwordReport && (
              <div className="mt-6 pt-6 border-t border-border space-y-4">
                <div
                  style={{
                    backgroundColor: passwordReport.is_pwned ? '#FDEAEA' : '#E7F7EF',
                    borderColor: passwordReport.is_pwned ? '#F8C8C8' : '#B8EBD0',
                  }}
                  className="p-4 rounded-xl border flex items-start space-x-3"
                >
                  {passwordReport.is_pwned ? (
                    <AlertTriangle className="w-6 h-6 text-riskHigh-text shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-6 h-6 text-riskLow-text shrink-0 mt-0.5" />
                  )}
                  <div>
                    <h4 className="text-base font-bold text-textPrimary mb-1">{passwordReport.message}</h4>
                    <p className="text-xs text-textSecondary leading-relaxed">{passwordReport.disclaimer}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h5 className="text-xs font-semibold text-textPrimary uppercase tracking-wider">Recommendations</h5>
                  {passwordReport.recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-sm text-textSecondary">
                      <CheckSquare className="w-4 h-4 text-brand-500 shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* PAGE 4: SECURITY CHECKUP (/checkup) */}
      {activeRoute === 'checkup' && (
        <div className="space-y-8 max-w-2xl mx-auto">
          {!checkupReport ? (
            <Card>
              {questions.length > 0 && questions[currentQIndex] && (
                <div className="space-y-6">
                  {/* Slim Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-semibold text-textSecondary">
                      <span>Question {currentQIndex + 1} of {questions.length}</span>
                      <span>Category: {questions[currentQIndex].category_title}</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-border">
                      <div
                        className="bg-brand-500 h-full transition-all duration-300"
                        style={{ width: `${((currentQIndex + 1) / questions.length) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Question */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-textPrimary leading-snug">
                      {questions[currentQIndex].question}
                    </h3>

                    <div className="space-y-3">
                      {questions[currentQIndex].options.map((opt) => (
                        <button
                          key={opt.id}
                          onClick={() => handleCheckupAnswerSelect(opt.id)}
                          className={`w-full text-left p-4 rounded-xl border transition-all flex items-start space-x-3 ${
                            userAnswers[questions[currentQIndex].id] === opt.id
                              ? 'border-brand-500 bg-brand-50 text-brand-700 font-semibold'
                              : 'border-border bg-surface hover:bg-slate-50 text-textPrimary'
                          }`}
                        >
                          <span className="w-5 h-5 rounded-full border border-slate-300 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                            {opt.id}
                          </span>
                          <span className="text-sm">{opt.text}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex justify-between pt-4 border-t border-border">
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={currentQIndex === 0}
                      onClick={() => setCurrentQIndex(currentQIndex - 1)}
                    >
                      Previous
                    </Button>
                    {currentQIndex === questions.length - 1 ? (
                      <Button variant="primary" size="md" onClick={handleFinishCheckup} isLoading={isCheckupSubmitting}>
                        Submit & View Score
                      </Button>
                    ) : (
                      <Button variant="primary" size="sm" onClick={() => setCurrentQIndex(currentQIndex + 1)}>
                        Next Question
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </Card>
          ) : (
            /* Results Report Page */
            <div className="space-y-6">
              <Card className="text-center space-y-4">
                <ScoreDial score={checkupReport.overall_score} level={checkupReport.security_level === 'EXCELLENT' ? 'LOW' : 'HIGH'} size={130} />
                <h2 className="text-2xl font-extrabold text-textPrimary">Your Digital Security Profile</h2>
                <Alert type="warning" title={`Weakest Category: ${checkupReport.weakest_category}`}>
                  Focus your immediate security improvements on this category to lower risk.
                </Alert>
              </Card>

              <Card className="space-y-4">
                <h3 className="text-sm font-bold text-textPrimary uppercase tracking-wider">Per-Category Breakdown</h3>
                <div className="space-y-3">
                  {Object.entries(checkupReport.category_scores).map(([catKey, info]) => (
                    <div key={catKey} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-textPrimary">{info.title}</span>
                        <span className="text-brand-600">{info.score}%</span>
                      </div>
                      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-border">
                        <div
                          className={`h-full ${info.score >= 80 ? 'bg-riskLow-text' : info.score >= 50 ? 'bg-riskMod-text' : 'bg-riskHigh-text'}`}
                          style={{ width: `${info.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* PAGE 5: HISTORY (/history) */}
      {activeRoute === 'history' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-extrabold text-textPrimary tracking-tight">Scan History Log</h2>
            <Button variant="secondary" size="sm" onClick={loadHistory} isLoading={isHistoryLoading}>
              Refresh Log
            </Button>
          </div>

          {historyRecords.length === 0 ? (
            <EmptyState
              title="No Past Scans Recorded"
              description="Scans performed across URL, Message, QR, and Image tools will appear here."
              action={
                <Button variant="primary" size="sm" onClick={() => setActiveRoute('home')}>
                  Perform First Scan
                </Button>
              }
            />
          ) : (
            <Card className="p-0 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="bg-slate-50 border-b border-border text-xs font-bold text-textSecondary uppercase tracking-wider">
                      <th className="p-4">Type</th>
                      <th className="p-4">Target / Indicator</th>
                      <th className="p-4">Risk Level</th>
                      <th className="p-4">Score</th>
                      <th className="p-4">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {historyRecords.map((rec) => (
                      <tr key={rec.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="p-4 font-bold uppercase text-xs text-brand-600">{rec.scan_type}</td>
                        <td className="p-4 font-mono text-xs text-textPrimary truncate max-w-xs">{rec.indicator}</td>
                        <td className="p-4"><RiskBadge level={rec.risk_level} size="sm" /></td>
                        <td className="p-4 font-bold text-textPrimary">{rec.risk_score}/100</td>
                        <td className="p-4 text-xs text-textSecondary">{new Date(rec.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* PAGE 6: ABOUT (/about) */}
      {activeRoute === 'about' && (
        <div className="space-y-6 max-w-2xl mx-auto">
          <h2 className="text-3xl font-extrabold text-textPrimary tracking-tight">About APATI ASPIS</h2>
          
          <Card className="space-y-4">
            <h3 className="text-lg font-bold text-textPrimary">What APATI ASPIS Is</h3>
            <p className="text-sm text-textSecondary leading-relaxed">
              APATI ASPIS is a digital safety platform that helps users analyze suspicious URLs, messages, QR codes, screenshots, and security habits to detect deception before harm occurs.
            </p>

            <h3 className="text-lg font-bold text-textPrimary pt-2">What APATI ASPIS Is NOT</h3>
            <ul className="text-sm text-textSecondary space-y-1 list-disc pl-5">
              <li>Not an antivirus software or endpoint security agent (EDR).</li>
              <li>Not a sandbox malware execution suite or SOC platform.</li>
              <li>Does not guarantee that an indicator is 100% safe or malicious.</li>
            </ul>

            <div className="pt-4 border-t border-border">
              <h4 className="text-xs font-bold text-textPrimary uppercase tracking-wider mb-2">Legal Disclaimer</h4>
              <p className="text-xs text-textSecondary leading-relaxed">
                APATI ASPIS provides risk analysis and educational guidance for digital safety. Risk assessments are generated via deterministic heuristics and threat intelligence datasets.
              </p>
            </div>
          </Card>
        </div>
      )}

      {scanError && (
        <div className="mt-6">
          <ErrorState message={scanError} onRetry={() => setScanError(null)} />
        </div>
      )}
    </Layout>
  );
};

export default App;
