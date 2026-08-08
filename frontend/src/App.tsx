import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RiskBadge } from './components/RiskBadge';
import { Alert } from './components/Alert';
import { Button } from './components/Button';
import { Input } from './components/Input';
import { Card } from './components/Card';
import {
  fetchHealth, scanUrl, scanMessage, scanQrFile, scanImageFile,
  fetchCheckupQuestions, submitCheckup, fetchScanHistory, checkPassword,
  HealthResponse, CheckupQuestion, CheckupReport, ScanRecordHistory, PasswordCheckResponse
} from './services/api';
import {
  Search, ShieldAlert, FileText, QrCode, Image as ImageIcon,
  AlertTriangle, CheckSquare, Lightbulb, Info, Upload, ShieldCheck, Award, History, Clock, KeyRound, Lock
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'url' | 'message' | 'qr' | 'image' | 'checkup' | 'history' | 'password'>('url');
  const [inputContent, setInputContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState<boolean>(true);

  // Scan state
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);

  // Checkup state
  const [questions, setQuestions] = useState<CheckupQuestion[]>([]);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [checkupReport, setCheckupReport] = useState<CheckupReport | null>(null);
  const [isCheckupSubmitting, setIsCheckupSubmitting] = useState<boolean>(false);

  // History state
  const [historyRecords, setHistoryRecords] = useState<ScanRecordHistory[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  // Password check state
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordReport, setPasswordReport] = useState<PasswordCheckResponse | null>(null);
  const [isPasswordChecking, setIsPasswordChecking] = useState<boolean>(false);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealthStatus(data);
        setHealthError(null);
      })
      .catch((err) => {
        setHealthError(err.message || 'Failed to connect to backend server');
      })
      .finally(() => {
        setIsHealthLoading(false);
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
    } catch (err: any) {
      setScanError('Failed to load scan history');
    } finally {
      setIsHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history') {
      loadHistory();
    }
  }, [activeTab]);

  const handleScan = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    setIsScanning(true);
    setScanError(null);
    setScanResult(null);

    try {
      if (activeTab === 'url') {
        if (!inputContent.trim()) throw new Error('Please enter a target URL.');
        const res = await scanUrl(inputContent.trim());
        setScanResult(res);
      } else if (activeTab === 'message') {
        if (!inputContent.trim()) throw new Error('Please enter message content.');
        const res = await scanMessage(inputContent.trim());
        setScanResult(res);
      } else if (activeTab === 'qr') {
        if (!selectedFile) throw new Error('Please select a QR image file.');
        const res = await scanQrFile(selectedFile);
        setScanResult(res);
      } else if (activeTab === 'image') {
        if (!selectedFile) throw new Error('Please select a screenshot or image file.');
        const res = await scanImageFile(selectedFile);
        setScanResult(res);
      }
    } catch (err: any) {
      setScanError(err.message || 'An error occurred during analysis.');
    } finally {
      setIsScanning(false);
    }
  };

  const handlePasswordCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordInput) return;

    setIsPasswordChecking(true);
    setScanError(null);
    setPasswordReport(null);

    try {
      const res = await checkPassword(passwordInput);
      setPasswordReport(res);
    } catch (err: any) {
      setScanError(err.message || 'Failed to check password');
    } finally {
      setIsPasswordChecking(false);
    }
  };

  const handleCheckupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCheckupSubmitting(true);
    try {
      const report = await submitCheckup(userAnswers);
      setCheckupReport(report);
    } catch (err: any) {
      setScanError(err.message || 'Failed to evaluate checkup');
    } finally {
      setIsCheckupSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Header />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-12">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-extrabold tracking-tight text-slate-100 sm:text-4xl mb-3">
            Detect Deception Before It Strikes
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Analyze suspicious URLs, text messages, QR codes, screenshots, password breach safety, or complete your Security Checkup.
          </p>
        </div>

        {/* Backend Connection Status Banner */}
        <div className="mb-8">
          {isHealthLoading ? (
            <Alert type="info" title="Backend Connection">
              Connecting to APATI ASPIS API server...
            </Alert>
          ) : healthError ? (
            <Alert type="warning" title="Backend Status">
              {healthError} (Ensure backend server is running on http://localhost:8000)
            </Alert>
          ) : (
            <Alert type="success" title="Backend Connected">
              Connected to <strong>{healthStatus?.service}</strong> (v{healthStatus?.version} — {healthStatus?.environment} mode)
            </Alert>
          )}
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex justify-center border-b border-slate-800 mb-8 overflow-x-auto">
          <button
            onClick={() => { setActiveTab('url'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'url' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>URL Scanner</span>
          </button>
          <button
            onClick={() => { setActiveTab('message'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'message' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Message / Text</span>
          </button>
          <button
            onClick={() => { setActiveTab('qr'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'qr' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <QrCode className="w-4 h-4" />
            <span>QR Code</span>
          </button>
          <button
            onClick={() => { setActiveTab('image'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'image' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            <span>Image / Screenshot</span>
          </button>
          <button
            onClick={() => { setActiveTab('password'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'password' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <KeyRound className="w-4 h-4" />
            <span>Password Check</span>
          </button>
          <button
            onClick={() => { setActiveTab('checkup'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'checkup' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Security Checkup</span>
          </button>
          <button
            onClick={() => { setActiveTab('history'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'history' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <History className="w-4 h-4" />
            <span>Scan History</span>
          </button>
        </div>

        {/* Input Form Card for URL, Message, QR, Image */}
        {activeTab !== 'checkup' && activeTab !== 'history' && activeTab !== 'password' && (
          <Card className="mb-8">
            <form onSubmit={handleScan} className="space-y-4">
              {activeTab === 'url' || activeTab === 'message' ? (
                <div className="flex gap-3 items-end">
                  {activeTab === 'url' ? (
                    <Input
                      label="Enter URL to analyze"
                      value={inputContent}
                      onChange={(e) => setInputContent(e.target.value)}
                      placeholder="https://example.com"
                    />
                  ) : (
                    <div className="w-full">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Paste SMS, Email, or Chat message</label>
                      <textarea
                        rows={3}
                        value={inputContent}
                        onChange={(e) => setInputContent(e.target.value)}
                        placeholder="Paste suspicious text message or email content here..."
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm"
                      />
                    </div>
                  )}
                  <Button variant="primary" type="submit" isLoading={isScanning}>
                    Analyze Risk
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <div className="flex-1 w-full">
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      {activeTab === 'qr' ? 'Upload QR Code Image' : 'Upload Screenshot or Picture'}
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-600 file:text-white hover:file:bg-sky-500 cursor-pointer bg-slate-950 border border-slate-800 p-2 rounded-lg"
                    />
                  </div>
                  <Button variant="primary" type="submit" isLoading={isScanning} className="w-full sm:w-auto">
                    <Upload className="w-4 h-4 mr-2" /> Upload & Analyze
                  </Button>
                </div>
              )}
            </form>
          </Card>
        )}

        {/* Password Check Form View */}
        {activeTab === 'password' && (
          <div className="space-y-6 mb-8">
            <Card className="border-slate-700">
              <h3 className="text-xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <KeyRound className="w-6 h-6 text-sky-400" /> Password Breach Checker (K-Anonymity)
              </h3>
              <p className="text-sm text-slate-400 mb-6">
                Checks if your password has appeared in public data breaches. Uses <strong>K-Anonymity privacy protection</strong> — your plaintext password is <strong>never</strong> transmitted over the internet or saved to a database.
              </p>

              <form onSubmit={handlePasswordCheck} className="flex gap-3 items-end mb-6">
                <div className="w-full">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Enter password to test</label>
                  <input
                    type="password"
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    placeholder="Enter password..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 text-sm font-mono"
                  />
                </div>
                <Button variant="primary" type="submit" isLoading={isPasswordChecking}>
                  Check Breach Safety
                </Button>
              </form>

              {passwordReport && (
                <div className="space-y-4 border-t border-slate-800 pt-6">
                  <div className={`p-4 rounded-lg border ${passwordReport.is_pwned ? 'bg-rose-950/30 border-rose-800/60' : 'bg-emerald-950/30 border-emerald-800/60'}`}>
                    <div className="flex items-center space-x-3 mb-2">
                      {passwordReport.is_pwned ? (
                        <AlertTriangle className="w-6 h-6 text-rose-400" />
                      ) : (
                        <Lock className="w-6 h-6 text-emerald-400" />
                      )}
                      <h4 className="text-lg font-bold text-slate-100">{passwordReport.message}</h4>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed italic border-t border-slate-800/50 pt-2 mt-2">
                      {passwordReport.disclaimer}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Security Advice</h4>
                    <ul className="space-y-2">
                      {passwordReport.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-sm text-slate-300">
                          <CheckSquare className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Scan History View */}
        {activeTab === 'history' && (
          <Card className="mb-8 border-slate-700">
            <h3 className="text-xl font-bold text-slate-100 mb-2 flex items-center gap-2">
              <History className="w-6 h-6 text-sky-400" /> Recent Scan History
            </h3>
            <p className="text-sm text-slate-400 mb-6">
              Persisted scan results stored locally in SQLite database (`apati_aspis.db`).
            </p>

            {isHistoryLoading ? (
              <p className="text-sm text-slate-400 py-6 text-center">Loading scan history...</p>
            ) : historyRecords.length === 0 ? (
              <p className="text-sm text-slate-500 py-6 text-center">No scan history recorded yet.</p>
            ) : (
              <div className="space-y-3">
                {historyRecords.map((item) => (
                  <div key={item.id} className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-xs font-semibold uppercase bg-slate-800 text-sky-400 px-2 py-0.5 rounded">
                          {item.scan_type}
                        </span>
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {new Date(item.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-slate-200 truncate max-w-md">{item.indicator}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-black text-slate-100">{item.risk_score}<span className="text-xs text-slate-500">/100</span></span>
                      <RiskBadge level={item.risk_level} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* Security Checkup View */}
        {activeTab === 'checkup' && (
          <div className="space-y-6 mb-8">
            <Card className="border-slate-700">
              <h3 className="text-xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-sky-400" /> Digital Security Checkup
              </h3>
              <p className="text-sm text-slate-400 mb-6">
                Answer 12 security practice questions across 6 categories to receive your security score and personalized recommendations.
              </p>

              <form onSubmit={handleCheckupSubmit} className="space-y-6">
                {questions.map((q, qIdx) => (
                  <div key={q.id} className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider block mb-1">
                      Category {qIdx + 1}/12: {q.category_title}
                    </span>
                    <p className="text-sm font-semibold text-slate-200 mb-3">{q.question}</p>

                    <div className="space-y-2">
                      {q.options.map((opt) => (
                        <label
                          key={opt.id}
                          className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                            userAnswers[q.id] === opt.id
                              ? 'border-sky-500 bg-sky-950/20 text-sky-200'
                              : 'border-slate-800 hover:border-slate-700 text-slate-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name={`q_${q.id}`}
                            value={opt.id}
                            checked={userAnswers[q.id] === opt.id}
                            onChange={() => setUserAnswers({ ...userAnswers, [q.id]: opt.id })}
                            className="mt-0.5 text-sky-500 focus:ring-sky-500"
                          />
                          <span className="text-xs leading-relaxed">{opt.text}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}

                <Button variant="primary" type="submit" isLoading={isCheckupSubmitting} className="w-full">
                  Calculate Security Profile Score
                </Button>
              </form>
            </Card>

            {/* Checkup Results Report */}
            {checkupReport && (
              <Card className="border-sky-700 bg-slate-900/90">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                  <div className="flex items-center space-x-3">
                    <Award className="w-7 h-7 text-sky-400" />
                    <div>
                      <h3 className="text-xl font-bold text-slate-100">Security Profile Report</h3>
                      <p className="text-xs text-slate-400">Weakest Category: <strong className="text-amber-400">{checkupReport.weakest_category}</strong></p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-black text-slate-100">{checkupReport.overall_score}<span className="text-xs text-slate-500">/100</span></span>
                    <div className="text-xs font-bold text-sky-400 uppercase tracking-wider">{checkupReport.security_level}</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  {Object.entries(checkupReport.category_scores).map(([catKey, info]) => (
                    <div key={catKey} className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <div className="flex justify-between items-center text-xs font-medium mb-1">
                        <span className="text-slate-300">{info.title}</span>
                        <span className="font-bold text-sky-400">{info.score}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${info.score >= 80 ? 'bg-emerald-500' : info.score >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                          style={{ width: `${info.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Targeted Action Plan</h4>
                  <ul className="space-y-2">
                    {checkupReport.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-2 text-sm text-slate-200">
                        <CheckSquare className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Scan Error Banner */}
        {scanError && (
          <div className="mb-8">
            <Alert type="error" title="Analysis Notice">
              {scanError}
            </Alert>
          </div>
        )}

        {/* Live Analysis Result & Explanation Cards */}
        {scanResult && activeTab !== 'checkup' && activeTab !== 'history' && activeTab !== 'password' && (
          <div className="space-y-6 mb-8">
            <Card className="border-slate-700">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <ShieldAlert className="w-6 h-6 text-sky-400" />
                  <div>
                    <h3 className="text-xl font-bold text-slate-100">Security Assessment Report</h3>
                    <p className="text-xs text-slate-400">
                      Input Type: <span className="uppercase font-semibold">{activeTab}</span>
                      {scanResult.decoded_text && ` — Decoded: ${scanResult.decoded_text}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-2xl font-black text-slate-200">{scanResult.risk_score}<span className="text-xs text-slate-500">/100</span></span>
                  <RiskBadge level={scanResult.risk_level} />
                </div>
              </div>

              {/* Gemini Summary */}
              <div className="mb-6 bg-slate-950 p-4 rounded-lg border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-sky-400" /> Security Summary
                </h4>
                <p className="text-sm text-slate-200 leading-relaxed font-medium">
                  {scanResult.explanation?.summary}
                </p>
              </div>

              {/* Why Risky */}
              <div className="mb-6">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Why Is This Risky?</h4>
                <ul className="space-y-2">
                  {scanResult.explanation?.why_risky?.map((item: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2 text-sm text-slate-300">
                      <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommended Actions */}
              <div className="mb-6">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Recommended Actions</h4>
                <ul className="space-y-2">
                  {scanResult.explanation?.recommended_actions?.map((action: string, idx: number) => (
                    <li key={idx} className="flex items-start space-x-2 text-sm text-slate-300">
                      <CheckSquare className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Educational Tips */}
              {scanResult.explanation?.education && scanResult.explanation.education.length > 0 && (
                <div className="mb-6 bg-sky-950/20 border border-sky-800/40 p-4 rounded-lg">
                  <h4 className="text-xs font-semibold text-sky-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Lightbulb className="w-4 h-4 text-sky-400" /> Educational Advice
                  </h4>
                  <ul className="space-y-1 text-xs text-sky-200">
                    {scanResult.explanation.education.map((tip: string, idx: number) => (
                      <li key={idx}>• {tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        APATI ASPIS — Digital Safety Platform. Risk analysis provided for educational purposes.
      </footer>
    </div>
  );
};

export default App;
