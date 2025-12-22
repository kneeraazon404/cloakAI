import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
    const [selectedFiles, setSelectedFiles] = useState(null);
    const [mode, setMode] = useState('low');
    const [format, setFormat] = useState('png'); // New format state
    const [taskId, setTaskId] = useState(null);
    const [status, setStatus] = useState('IDLE');
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState(["System Ready. Waiting for input... (v1.0.2)"]);
    const [startTime, setStartTime] = useState(null);
    const [elapsed, setElapsed] = useState(0);

    const fileInputRef = useRef(null);
    const logsEndRef = useRef(null);

    // Auto-scroll logs
    useEffect(() => {
        if (logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [logs]);

    // Timer logic
    useEffect(() => {
        let timer;
        if ((status === 'UPLOADING' || status === 'PROCESSING') && startTime) {
            timer = setInterval(() => {
                const now = Date.now();
                setElapsed(Math.floor((now - startTime) / 1000));
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [status, startTime]);

    const addLog = (msg) => {
        const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
        setLogs(prev => [...prev, `[${timestamp}] ${msg}`]);
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(e.target.files);
            addLog(`Targets acquired: ${e.target.files.length} file(s). Select parameters.`);
            setStatus('IDLE');
            setProgress(0);
            setElapsed(0);
        }
    };

    const getEstimatedTime = () => {
        if (!selectedFiles) return 0;
        const perImg = mode === 'low' ? 20 : mode === 'mid' ? 45 : 90;
        return perImg * selectedFiles.length;
    };

    const handleUpload = async () => {
        if (!selectedFiles) return;

        const formData = new FormData();
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('files', selectedFiles[i]);
        }

        try {
            setStatus('UPLOADING');
            setStartTime(Date.now());
            setElapsed(0);
            addLog("Initiating secure upload...");
            setProgress(10);

            // Pass format in query param
            const response = await axios.post(`${API_URL}/protect?mode=${mode}&format=${format}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            setTaskId(response.data.task_id);
            setStatus('PROCESSING');
            addLog(`Upload complete. Task ID: ${response.data.task_id.substring(0, 8)}...`);
            addLog(`Engaging cloaking sequence (Level: ${mode.toUpperCase()}, Format: ${format.toUpperCase()})...`);
            setProgress(20);
        } catch (err) {
            console.error(err);
            setStatus('ERROR');
            addLog("CRITICAL: Upload Negotiation Failed.");
            setProgress(0);
        }
    };

    // Polling & Sim
    useEffect(() => {
        let interval;
        let progressInterval;

        if (taskId && status === 'PROCESSING') {
            interval = setInterval(async () => {
                try {
                    const response = await axios.get(`${API_URL}/status/${taskId}`);
                    const taskStatus = response.data.status;
                    const result = response.data.result;

                    if (taskStatus === 'SUCCESS') {
                        if (result && (result.status === 1 || result.status === 'SUCCESS')) {
                            setStatus('COMPLETE');
                            const finalTime = result.elapsed_time || elapsed;
                            addLog(`Cloaking Sequence Complete. Total Time: ${finalTime}s`);
                            if (result.elapsed_time) setElapsed(Math.round(result.elapsed_time));
                            setProgress(100);
                            clearInterval(interval);
                        } else {
                            setStatus('ERROR');
                            const errMsg = result && result.error ? result.error : "Unknown logic error";
                            addLog(`ERR: ${errMsg}`);
                            clearInterval(interval);
                        }
                    } else if (taskStatus === 'FAILURE') {
                        setStatus('ERROR');
                        addLog("ERR: System Worker Crash.");
                        clearInterval(interval);
                    }
                } catch (err) { }
            }, 2000);

            const est = getEstimatedTime();
            progressInterval = setInterval(() => {
                setProgress(prev => {
                    const target = 95;
                    const step = 100 / (est * 2);
                    if (prev >= target) return target;
                    return prev + step;
                });
            }, 500);
        }
        return () => { clearInterval(interval); clearInterval(progressInterval); };
    }, [taskId, status]);

    const handleDownload = () => window.open(`${API_URL}/download/${taskId}`, '_blank');
    const triggerFileSelect = () => fileInputRef.current.click();

    return (
        <div className="App">
            <header className="App-header">
                <div className="brand-title">CLOAK<span style={{ color: 'var(--color-safe)' }}>AI</span></div>
                <span className="version-tag">DEFENSE_PLATFORM_V1</span>
            </header>

            <div className="security-panel">
                <div className="panel-header">
                    <span>STATUS: {status}</span>
                    <span>SEC_LEVEL: {mode.toUpperCase()}</span>
                </div>

                <div className="panel-body">
                    {/* INPUT SECTION */}
                    <div className="label-mono">01_TARGET_ACQUISITION</div>
                    <div className={`drop-target ${selectedFiles ? 'active' : ''}`} onClick={triggerFileSelect}>
                        <div className="icon-large" style={{ marginBottom: '0.5rem' }}>{selectedFiles ? '📁' : '⌖'}</div>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: 'bold' }}>
                            {selectedFiles ? `${selectedFiles.length} ASSETS SELECTED` : 'DROP ASSETS [SCAN]'}
                        </div>
                        <input ref={fileInputRef} type="file" style={{ display: 'none' }} multiple onChange={handleFileChange} accept="image/*" />
                    </div>

                    {/* SETTINGS */}
                    <div className="control-group">
                        <div className="label-mono">02_OBFUSCATION_PARAMETERS</div>

                        {/* Mode Selector */}
                        <div className="mode-grid" style={{ marginBottom: '20px' }}>
                            {['low', 'mid', 'high'].map(m => (
                                <div
                                    key={m}
                                    className={`mode-btn ${mode === m ? 'selected' : ''}`}
                                    onClick={() => setMode(m)}
                                >
                                    {m === 'low' ? 'STANDARD' : m === 'mid' ? 'ENHANCED' : 'MAXIMUM'}
                                </div>
                            ))}
                        </div>

                        {/* Format Selector */}
                        <div className="label-mono">03_OUTPUT_FORMAT</div>
                        <div className="mode-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                            {['png', 'jpg'].map(f => (
                                <div
                                    key={f}
                                    className={`mode-btn ${format === f ? 'selected' : ''}`}
                                    onClick={() => setFormat(f)}
                                >
                                    {f.toUpperCase()}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* EXECUTE */}
                    <button
                        className="btn-execute"
                        onClick={status === 'COMPLETE' ? handleDownload : handleUpload}
                        disabled={!selectedFiles || status === 'UPLOADING' || status === 'PROCESSING'}
                        style={{
                            background: status === 'COMPLETE' ? 'var(--color-safe)' : status === 'ERROR' ? 'var(--color-danger)' : ''
                        }}
                    >
                        {status === 'UPLOADING' ? 'UPLOADING...' :
                            status === 'PROCESSING' ? 'CLOAKING...' :
                                status === 'COMPLETE' ? 'DOWNLOAD ARTIFACTS' :
                                    status === 'ERROR' ? 'SYSTEM FAILURE' :
                                        'INITIATE CLOAKING'}
                    </button>

                    {/* CONSOLE */}
                    <div className="console-output">
                        {logs.map((log, i) => (
                            <div key={i} className="console-line">{log}</div>
                        ))}
                        <div ref={logsEndRef} />
                    </div>
                    {status !== 'IDLE' && (
                        <div >
                            <div className="progress-bar-container">
                                <div className="progress-fill" style={{ width: `${Math.min(progress, 100)}%`, background: status === 'ERROR' ? 'var(--color-danger)' : 'var(--color-safe)' }}></div>
                            </div>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                fontFamily: 'var(--font-mono)',
                                fontSize: '0.8rem',
                                color: 'var(--text-dim)',
                                marginTop: '8px'
                            }}>
                                <span>{status === 'COMPLETE' ? `TOTAL TIME: ${elapsed}s` : `ELAPSED: ${elapsed}s`}</span>
                                <span>{Math.round(progress)}%</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
