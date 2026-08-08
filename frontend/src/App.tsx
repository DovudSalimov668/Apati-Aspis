import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { RiskBadge } from './components/RiskBadge';
import { Alert } from './components/Alert';
import { Button } from './components/Button';
import { Input } from './components/Input';
import { Card } from './components/Card';
import { fetchHealth, scanUrl, scanMessage, scanQrFile, scanImageFile, HealthResponse } from './services/api';
import { Search, ShieldAlert, FileText, QrCode, Image as ImageIcon, AlertTriangle, CheckSquare, Lightbulb, Info, Upload } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'url' | 'message' | 'qr' | 'image'>('url');
  const [inputContent, setInputContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState<boolean>(true);

  // Scan state
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);

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
  }, []);

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

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Header />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-12">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-extrabold tracking-tight text-slate-100 sm:text-4xl mb-3">
            Detect Deception Before It Strikes
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Analyze suspicious URLs, text messages, QR codes, or screenshots to receive instant risk analysis and clear security advice.
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
            className={`flex items-center space-x-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'url'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>URL Scanner</span>
          </button>
          <button
            onClick={() => { setActiveTab('message'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'message'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Message / Text</span>
          </button>
          <button
            onClick={() => { setActiveTab('qr'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'qr'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <QrCode className="w-4 h-4" />
            <span>QR Code</span>
          </button>
          <button
            onClick={() => { setActiveTab('image'); setScanResult(null); }}
            className={`flex items-center space-x-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'image'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            <span>Image / Screenshot</span>
          </button>
        </div>

        {/* Input Form Card */}
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

        {/* Scan Error Banner */}
        {scanError && (
          <div className="mb-8">
            <Alert type="error" title="Analysis Notice">
              {scanError}
            </Alert>
          </div>
        )}

        {/* Live Analysis Result & Explanation Cards */}
        {scanResult && (
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
