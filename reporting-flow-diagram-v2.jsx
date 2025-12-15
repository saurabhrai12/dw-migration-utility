import React from 'react';

const ReportingFlowDiagram = () => {
  // Color schemes matching the Mermaid styles
  const styles = {
    storage: { bg: '#e1f5fe', border: '#01579b', text: '#01579b' },
    process: { bg: '#fff3e0', border: '#e65100', text: '#e65100' },
    external: { bg: '#f3e5f5', border: '#4a148c', text: '#4a148c' },
    control: { bg: '#e8f5e9', border: '#1b5e20', text: '#1b5e20' },
    event: { bg: '#fef3c7', border: '#d97706', text: '#92400e' },
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-center mb-2 text-gray-800">
        Enterprise Reporting Solution Architecture
      </h1>
      <p className="text-center text-gray-500 mb-6 text-sm">
        Event-Driven Report Generation & Distribution Platform
      </p>

      <svg viewBox="0 0 1100 920" className="w-full max-w-5xl mx-auto">
        <defs>
          {/* Arrow markers */}
          <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
          <marker id="arrow-dashed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
          </marker>
          <marker id="arrow-event" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#d97706" />
          </marker>
          
          {/* Drop shadow */}
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="1" dy="2" stdDeviation="2" floodOpacity="0.15"/>
          </filter>
        </defs>

        {/* ==================== SUBGRAPH BACKGROUNDS ==================== */}
        
        {/* Input Source */}
        <rect x="20" y="20" width="200" height="100" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="120" y="45" textAnchor="middle" className="text-xs font-semibold" fill="#64748b">Input Source</text>

        {/* Control Plane */}
        <rect x="340" y="170" width="220" height="140" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="450" y="195" textAnchor="middle" className="text-xs font-semibold" fill="#64748b">Control Plane</text>

        {/* Report Generation Engines */}
        <rect x="620" y="170" width="460" height="200" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="850" y="195" textAnchor="middle" className="text-xs font-semibold" fill="#64748b">Report Generation Engines</text>

        {/* S3 Event Bridge Section */}
        <rect x="450" y="420" width="320" height="120" rx="8" fill="#fffbeb" stroke="#d97706" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="610" y="445" textAnchor="middle" className="text-xs font-semibold" fill="#92400e">S3 Event Trigger Zone</text>

        {/* Distribution Layer */}
        <rect x="20" y="540" width="200" height="100" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="120" y="565" textAnchor="middle" className="text-xs font-semibold" fill="#64748b">Distribution Layer</text>

        {/* Notifications */}
        <rect x="20" y="740" width="200" height="100" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="120" y="765" textAnchor="middle" className="text-xs font-semibold" fill="#64748b">Notifications</text>

        {/* ==================== NODES ==================== */}

        {/* Snowflake Worktable - Storage */}
        <g filter="url(#shadow)">
          <rect x="50" y="60" width="140" height="50" rx="6" fill={styles.storage.bg} stroke={styles.storage.border} strokeWidth="2"/>
          <text x="120" y="82" textAnchor="middle" className="text-xs font-medium" fill={styles.storage.text}>📊 Snowflake</text>
          <text x="120" y="98" textAnchor="middle" className="text-xs" fill={styles.storage.text}>Worktable</text>
        </g>

        {/* Request Poller Service - Process */}
        <g filter="url(#shadow)">
          <rect x="50" y="170" width="140" height="50" rx="6" fill={styles.process.bg} stroke={styles.process.border} strokeWidth="2"/>
          <text x="120" y="192" textAnchor="middle" className="text-xs font-medium" fill={styles.process.text}>⚙️ Request Poller</text>
          <text x="120" y="208" textAnchor="middle" className="text-xs" fill={styles.process.text}>Service</text>
        </g>

        {/* Message Queue - Control */}
        <g filter="url(#shadow)">
          <rect x="50" y="280" width="140" height="50" rx="6" fill={styles.control.bg} stroke={styles.control.border} strokeWidth="2"/>
          <text x="120" y="302" textAnchor="middle" className="text-xs font-medium" fill={styles.control.text}>📨 Message Queue</text>
          <text x="120" y="318" textAnchor="middle" className="text-xs" fill={styles.control.text}>Event Bus</text>
        </g>

        {/* Workflow Orchestrator - Control */}
        <g filter="url(#shadow)">
          <rect x="360" y="210" width="140" height="50" rx="6" fill={styles.control.bg} stroke={styles.control.border} strokeWidth="2"/>
          <text x="430" y="232" textAnchor="middle" className="text-xs font-medium" fill={styles.control.text}>🎯 Workflow</text>
          <text x="430" y="248" textAnchor="middle" className="text-xs" fill={styles.control.text}>Orchestrator</text>
        </g>

        {/* Audit & Status DB - Storage (cylinder shape) */}
        <g filter="url(#shadow)">
          <ellipse cx="430" cy="280" rx="50" ry="10" fill={styles.storage.bg} stroke={styles.storage.border} strokeWidth="2"/>
          <rect x="380" y="280" width="100" height="30" fill={styles.storage.bg} stroke={styles.storage.border} strokeWidth="2" strokeDasharray="0,50,100,0"/>
          <line x1="380" y1="280" x2="380" y2="310" stroke={styles.storage.border} strokeWidth="2"/>
          <line x1="480" y1="280" x2="480" y2="310" stroke={styles.storage.border} strokeWidth="2"/>
          <ellipse cx="430" cy="310" rx="50" ry="10" fill={styles.storage.bg} stroke={styles.storage.border} strokeWidth="2"/>
          <text x="430" y="298" textAnchor="middle" className="text-xs font-medium" fill={styles.storage.text}>Audit DB</text>
        </g>

        {/* Engine Router - Diamond */}
        <g filter="url(#shadow)">
          <polygon points="680,255 730,220 780,255 730,290" fill={styles.control.bg} stroke={styles.control.border} strokeWidth="2"/>
          <text x="730" y="252" textAnchor="middle" className="text-xs font-medium" fill={styles.control.text}>Engine</text>
          <text x="730" y="266" textAnchor="middle" className="text-xs" fill={styles.control.text}>Router</text>
        </g>

        {/* OBIEE Worker - External */}
        <g filter="url(#shadow)">
          <rect x="850" y="210" width="120" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="910" y="235" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>📊 OBIEE Worker</text>
        </g>

        {/* Power BI Worker - External */}
        <g filter="url(#shadow)">
          <rect x="850" y="260" width="120" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="910" y="285" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>📈 Power BI Worker</text>
        </g>

        {/* MIDAs Worker - External */}
        <g filter="url(#shadow)">
          <rect x="850" y="310" width="120" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="910" y="335" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>🔧 MIDAs Worker</text>
        </g>

        {/* S3 Staging Bucket - Storage */}
        <g filter="url(#shadow)">
          <rect x="470" y="460" width="140" height="60" rx="6" fill={styles.storage.bg} stroke={styles.storage.border} strokeWidth="2"/>
          <text x="540" y="485" textAnchor="middle" className="text-xs font-medium" fill={styles.storage.text}>☁️ S3 Staging</text>
          <text x="540" y="500" textAnchor="middle" className="text-xs" fill={styles.storage.text}>Bucket</text>
          <text x="540" y="514" textAnchor="middle" className="text-xs" fill="#d97706">⚡ Event Enabled</text>
        </g>

        {/* S3 Event / EventBridge - Event */}
        <g filter="url(#shadow)">
          <rect x="640" y="460" width="120" height="60" rx="6" fill={styles.event.bg} stroke={styles.event.border} strokeWidth="2"/>
          <text x="700" y="482" textAnchor="middle" className="text-xs font-medium" fill={styles.event.text}>⚡ S3 Event</text>
          <text x="700" y="498" textAnchor="middle" className="text-xs" fill={styles.event.text}>EventBridge /</text>
          <text x="700" y="512" textAnchor="middle" className="text-xs" fill={styles.event.text}>Lambda Trigger</text>
        </g>

        {/* Distribution Worker - Process */}
        <g filter="url(#shadow)">
          <rect x="50" y="580" width="140" height="50" rx="6" fill={styles.process.bg} stroke={styles.process.border} strokeWidth="2"/>
          <text x="120" y="602" textAnchor="middle" className="text-xs font-medium" fill={styles.process.text}>📤 Distribution</text>
          <text x="120" y="618" textAnchor="middle" className="text-xs" fill={styles.process.text}>Worker</text>
        </g>

        {/* Distribution Targets */}
        {/* FTP Server */}
        <g filter="url(#shadow)">
          <rect x="280" y="520" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="545" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>📁 FTP Server</text>
        </g>

        {/* NAS */}
        <g filter="url(#shadow)">
          <rect x="280" y="570" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="595" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>🗄️ NAS / Share</text>
        </g>

        {/* Target S3 */}
        <g filter="url(#shadow)">
          <rect x="280" y="620" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="645" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>☁️ Target S3</text>
        </g>

        {/* Email Gateway */}
        <g filter="url(#shadow)">
          <rect x="280" y="670" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="695" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>✉️ Email Gateway</text>
        </g>

        {/* Notification Service - Process */}
        <g filter="url(#shadow)">
          <rect x="50" y="780" width="140" height="50" rx="6" fill={styles.process.bg} stroke={styles.process.border} strokeWidth="2"/>
          <text x="120" y="802" textAnchor="middle" className="text-xs font-medium" fill={styles.process.text}>🔔 Notification</text>
          <text x="120" y="818" textAnchor="middle" className="text-xs" fill={styles.process.text}>Service</text>
        </g>

        {/* External MQ */}
        <g filter="url(#shadow)">
          <rect x="280" y="760" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="785" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>📨 External MQ</text>
        </g>

        {/* User Email */}
        <g filter="url(#shadow)">
          <rect x="280" y="810" width="110" height="40" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="335" y="835" textAnchor="middle" className="text-xs font-medium" fill={styles.external.text}>📧 User Email</text>
        </g>

        {/* ==================== ARROWS & LABELS ==================== */}

        {/* 1. Poller -> Snowflake (Fetch New Requests) */}
        <line x1="120" y1="170" x2="120" y2="115" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="130" y="130" width="95" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="177" y="140" textAnchor="middle" className="text-xs" fill="#64748b">1. Fetch New</text>
        <text x="177" y="152" textAnchor="middle" className="text-xs" fill="#64748b">Requests</text>

        {/* 2. Poller -> Kafka (Publish Job) */}
        <line x1="120" y1="220" x2="120" y2="275" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="130" y="235" width="70" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="165" y="245" textAnchor="middle" className="text-xs" fill="#64748b">2. Publish</text>
        <text x="165" y="257" textAnchor="middle" className="text-xs" fill="#64748b">Job</text>

        {/* 3. Kafka -> Orchestrator (Consume Job) */}
        <line x1="190" y1="305" x2="300" y2="305" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="300" y1="305" x2="300" y2="235" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="300" y1="235" x2="355" y2="235" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="220" y="280" width="70" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="255" y="290" textAnchor="middle" className="text-xs" fill="#64748b">3. Consume</text>
        <text x="255" y="302" textAnchor="middle" className="text-xs" fill="#64748b">Job</text>

        {/* Orchestrator -> AuditDB (Update Status) */}
        <line x1="430" y1="260" x2="430" y2="268" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="485" y="250" width="90" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="530" y="260" textAnchor="middle" className="text-xs" fill="#64748b">Update Status:</text>
        <text x="530" y="272" textAnchor="middle" className="text-xs font-medium" fill="#f59e0b">IN_PROGRESS</text>

        {/* 4. Orchestrator -> Router (Route Request) */}
        <line x1="500" y1="235" x2="675" y2="255" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="540" y="220" width="80" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="580" y="230" textAnchor="middle" className="text-xs" fill="#64748b">4. Route</text>
        <text x="580" y="242" textAnchor="middle" className="text-xs" fill="#64748b">Request</text>

        {/* Router -> OBIEE */}
        <line x1="780" y1="240" x2="845" y2="230" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="810" y="225" className="text-xs" fill="#64748b">OBIEE</text>

        {/* Router -> PowerBI */}
        <line x1="780" y1="255" x2="845" y2="280" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="810" y="275" className="text-xs" fill="#64748b">PowerBI</text>

        {/* Router -> MIDAs */}
        <line x1="780" y1="270" x2="845" y2="330" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="810" y="310" className="text-xs" fill="#64748b">MIDAs</text>

        {/* 5. Workers -> S3 Staging */}
        <line x1="910" y1="250" x2="910" y2="400" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="910" y1="400" x2="540" y2="400" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="540" y1="400" x2="540" y2="455" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <line x1="910" y1="300" x2="910" y2="400" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="910" y1="350" x2="910" y2="400" stroke="#64748b" strokeWidth="1.5"/>
        <rect x="750" y="380" width="80" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="790" y="390" textAnchor="middle" className="text-xs" fill="#64748b">5. Save</text>
        <text x="790" y="402" textAnchor="middle" className="text-xs" fill="#64748b">Output</text>

        {/* 6. S3 -> S3 Event (Event Trigger) - NEW */}
        <line x1="610" y1="490" x2="635" y2="490" stroke="#d97706" strokeWidth="2" markerEnd="url(#arrow-event)"/>
        <rect x="575" y="525" width="90" height="28" rx="4" fill="#fef3c7" stroke="#d97706" strokeWidth="1"/>
        <text x="620" y="535" textAnchor="middle" className="text-xs font-medium" fill="#92400e">6. S3 Event</text>
        <text x="620" y="547" textAnchor="middle" className="text-xs" fill="#92400e">Triggered</text>

        {/* 7. S3 Event -> Distribution Worker (Trigger Distribution) - NEW */}
        <line x1="700" y1="520" x2="700" y2="605" stroke="#d97706" strokeWidth="2"/>
        <line x1="700" y1="605" x2="195" y2="605" stroke="#d97706" strokeWidth="2" markerEnd="url(#arrow-event)"/>
        <rect x="400" y="580" width="100" height="28" rx="4" fill="#fef3c7" stroke="#d97706" strokeWidth="1"/>
        <text x="450" y="590" textAnchor="middle" className="text-xs font-medium" fill="#92400e">7. Trigger</text>
        <text x="450" y="602" textAnchor="middle" className="text-xs" fill="#92400e">Distribution</text>

        {/* Distribution Worker -> FTP */}
        <line x1="190" y1="590" x2="275" y2="540" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="220" y="555" className="text-xs" fill="#64748b">FTP</text>

        {/* Distribution Worker -> NAS */}
        <line x1="190" y1="600" x2="275" y2="590" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="220" y="585" className="text-xs" fill="#64748b">SMB/NFS</text>

        {/* Distribution Worker -> S3 */}
        <line x1="190" y1="610" x2="275" y2="640" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="220" y="635" className="text-xs" fill="#64748b">S3</text>

        {/* Distribution Worker -> Email */}
        <line x1="190" y1="620" x2="275" y2="690" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="220" y="680" className="text-xs" fill="#64748b">SMTP</text>

        {/* 8. Distribution Worker -> Notification Service */}
        <line x1="120" y1="630" x2="120" y2="775" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="130" y="690" width="80" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="170" y="700" textAnchor="middle" className="text-xs" fill="#64748b">8. Completion</text>
        <text x="170" y="712" textAnchor="middle" className="text-xs" fill="#64748b">Event</text>

        {/* Notification -> External MQ */}
        <line x1="190" y1="795" x2="275" y2="780" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="225" y="775" className="text-xs" fill="#64748b">Send Alert</text>

        {/* Notification -> User Email */}
        <line x1="190" y1="815" x2="275" y2="830" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <text x="225" y="835" className="text-xs" fill="#64748b">Send Email</text>

        {/* 9. Notification -> AuditDB */}
        <line x1="120" y1="780" x2="120" y2="740" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="120" y1="740" x2="500" y2="740" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="500" y1="740" x2="500" y2="310" stroke="#64748b" strokeWidth="1.5"/>
        <line x1="500" y1="310" x2="485" y2="310" stroke="#64748b" strokeWidth="1.5" markerEnd="url(#arrow)"/>
        <rect x="510" y="520" width="100" height="28" rx="4" fill="white" stroke="#e2e8f0" strokeWidth="1"/>
        <text x="560" y="530" textAnchor="middle" className="text-xs" fill="#64748b">9. Update Status:</text>
        <text x="560" y="542" textAnchor="middle" className="text-xs font-medium" fill="#10b981">COMPLETED/FAILED</text>

        {/* Optional: Notification -> Snowflake (dashed) */}
        <line x1="50" y1="805" x2="30" y2="805" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="5,3"/>
        <line x1="30" y1="805" x2="30" y2="85" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="5,3"/>
        <line x1="30" y1="85" x2="45" y2="85" stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="5,3" markerEnd="url(#arrow-dashed)"/>
        <text x="35" y="450" className="text-xs" fill="#94a3b8" transform="rotate(-90, 35, 450)">Optional: Write Back</text>

      </svg>

      {/* Legend */}
      <div className="mt-8 max-w-5xl mx-auto">
        <h3 className="text-sm font-semibold mb-3 text-gray-700">Legend</h3>
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-6 h-4 rounded" style={{ backgroundColor: styles.storage.bg, border: `2px solid ${styles.storage.border}` }}></div>
            <span className="text-gray-600">Storage</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-4 rounded" style={{ backgroundColor: styles.process.bg, border: `2px solid ${styles.process.border}` }}></div>
            <span className="text-gray-600">Process</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-4 rounded" style={{ backgroundColor: styles.control.bg, border: `2px solid ${styles.control.border}` }}></div>
            <span className="text-gray-600">Control</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-4 rounded" style={{ backgroundColor: styles.external.bg, border: `2px solid ${styles.external.border}` }}></div>
            <span className="text-gray-600">External</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-4 rounded" style={{ backgroundColor: styles.event.bg, border: `2px solid ${styles.event.border}` }}></div>
            <span className="text-gray-600">Event Trigger</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-gray-400"></div>
            <span className="text-gray-600">Data Flow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-amber-500"></div>
            <span className="text-gray-600">Event Flow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-0.5 bg-gray-300" style={{ backgroundImage: 'repeating-linear-gradient(90deg, #9ca3af 0, #9ca3af 4px, transparent 4px, transparent 8px)' }}></div>
            <span className="text-gray-600">Optional Flow</span>
          </div>
        </div>
      </div>

      {/* Flow Summary */}
      <div className="mt-6 max-w-5xl mx-auto bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold mb-3 text-gray-700">Workflow Steps</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-gray-600">
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">1</span>
            <span>Poller fetches new requests from Snowflake</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">2</span>
            <span>Job published to Message Queue</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">3</span>
            <span>Orchestrator consumes job</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">4</span>
            <span>Request routed to appropriate engine</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">5</span>
            <span>Report output saved to S3 staging</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-medium">6</span>
            <span><strong>S3 Event triggered</strong> on file landing</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-medium">7</span>
            <span><strong>Event triggers</strong> Distribution Worker</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">8</span>
            <span>Completion event sent to Notification</span>
          </div>
          <div className="flex gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-medium">9</span>
            <span>Final status updated in Audit DB</span>
          </div>
        </div>
      </div>

      {/* Architecture Note */}
      <div className="mt-4 max-w-5xl mx-auto bg-amber-50 rounded-lg p-4 border border-amber-200">
        <h3 className="text-sm font-semibold mb-2 text-amber-800">🔔 Event-Driven Distribution</h3>
        <p className="text-xs text-amber-700">
          The Distribution Worker is now triggered via <strong>S3 Event Notifications</strong> (EventBridge or Lambda trigger) 
          when report files land in the staging bucket. This decouples the orchestrator from distribution, 
          enabling automatic, real-time processing without polling and improving scalability.
        </p>
      </div>
    </div>
  );
};

export default ReportingFlowDiagram;
