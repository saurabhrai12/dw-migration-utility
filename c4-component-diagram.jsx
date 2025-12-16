import React from 'react';

const C4ComponentDiagram = () => {
  const styles = {
    container: { bg: '#438dd5', border: '#2e6295', text: '#ffffff' },
    component: { bg: '#85bbf0', border: '#5d9bd5', text: '#000000' },
    database: { bg: '#438dd5', border: '#2e6295', text: '#ffffff' },
    external: { bg: '#999999', border: '#7a7a7a', text: '#ffffff' },
    event: { bg: '#f59e0b', border: '#d97706', text: '#ffffff' },
  };

  return (
    <div className="p-6 bg-white min-h-screen">
      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Enterprise Reporting Solution</h1>
        <h2 className="text-lg text-blue-600 mt-1">Component Diagram (C4)</h2>
        <p className="text-sm text-gray-500 mt-2">Level 4: Shows the internal components and their interactions</p>
      </div>

      <svg viewBox="0 0 1400 1100" className="w-full max-w-7xl mx-auto">
        <defs>
          <marker id="arrow-c4" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666666" />
          </marker>
          <marker id="arrow-event" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#d97706" />
          </marker>
          <filter id="shadow-c4" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="3" stdDeviation="3" floodOpacity="0.2"/>
          </filter>
        </defs>

        {/* Title */}
        <text x="700" y="30" textAnchor="middle" className="text-sm font-bold" fill="#333">
          [Component Diagram] Enterprise Reporting Solution - Internal Architecture
        </text>

        {/* ==================== SYSTEM BOUNDARY ==================== */}
        <rect x="180" y="50" width="1040" height="980" rx="12" fill="none" stroke={styles.container.border} strokeWidth="3" strokeDasharray="10,5"/>
        <rect x="180" y="50" width="400" height="35" rx="8" fill={styles.container.bg}/>
        <text x="380" y="73" textAnchor="middle" className="text-sm font-bold" fill="white">Enterprise Reporting Solution [Software System]</text>

        {/* ==================== EXTERNAL ACTORS (LEFT SIDE) ==================== */}
        
        {/* Snowflake */}
        <g filter="url(#shadow-c4)">
          <rect x="20" y="200" width="130" height="80" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="85" y="230" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>📊 Snowflake</text>
          <text x="85" y="248" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External]</text>
          <text x="85" y="265" textAnchor="middle" className="text-xs" fill={styles.external.text}>Worktable</text>
        </g>

        {/* ==================== INGESTION LAYER ==================== */}
        
        <rect x="200" y="100" width="280" height="200" rx="8" fill="#e8f4fc" stroke="#438dd5" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="340" y="120" textAnchor="middle" className="text-xs font-semibold" fill="#2e6295">Ingestion Layer</text>

        {/* Request Poller */}
        <g filter="url(#shadow-c4)">
          <rect x="220" y="140" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="280" y="165" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Request</text>
          <text x="280" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Poller</text>
          <text x="280" y="198" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Request Validator */}
        <g filter="url(#shadow-c4)">
          <rect x="360" y="140" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="410" y="165" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Request</text>
          <text x="410" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Validator</text>
          <text x="410" y="198" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Job Publisher */}
        <g filter="url(#shadow-c4)">
          <rect x="280" y="220" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="340" y="245" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Job</text>
          <text x="340" y="260" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Publisher</text>
          <text x="340" y="278" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* ==================== MESSAGE QUEUE ==================== */}
        
        <g filter="url(#shadow-c4)">
          <rect x="280" y="320" width="120" height="60" rx="6" fill={styles.database.bg} stroke={styles.database.border} strokeWidth="2"/>
          <text x="340" y="345" textAnchor="middle" className="text-xs font-bold" fill={styles.database.text}>📨 Message</text>
          <text x="340" y="362" textAnchor="middle" className="text-xs font-bold" fill={styles.database.text}>Queue</text>
        </g>

        {/* ==================== ORCHESTRATION LAYER ==================== */}
        
        <rect x="500" y="100" width="400" height="280" rx="8" fill="#e8f4fc" stroke="#438dd5" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="700" y="120" textAnchor="middle" className="text-xs font-semibold" fill="#2e6295">Orchestration Layer</text>

        {/* Job Consumer */}
        <g filter="url(#shadow-c4)">
          <rect x="520" y="140" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="570" y="165" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Job</text>
          <text x="570" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Consumer</text>
          <text x="570" y="198" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Workflow Orchestrator */}
        <g filter="url(#shadow-c4)">
          <rect x="640" y="140" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="700" y="165" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Workflow</text>
          <text x="700" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Orchestrator</text>
          <text x="700" y="198" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Engine Router */}
        <g filter="url(#shadow-c4)">
          <rect x="780" y="140" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="830" y="165" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Engine</text>
          <text x="830" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Router</text>
          <text x="830" y="198" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Status Manager */}
        <g filter="url(#shadow-c4)">
          <rect x="520" y="230" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="570" y="255" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Status</text>
          <text x="570" y="270" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Manager</text>
          <text x="570" y="288" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Retry Handler */}
        <g filter="url(#shadow-c4)">
          <rect x="640" y="230" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="690" y="255" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Retry</text>
          <text x="690" y="270" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Handler</text>
          <text x="690" y="288" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Config Service */}
        <g filter="url(#shadow-c4)">
          <rect x="760" y="230" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="820" y="255" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Config</text>
          <text x="820" y="270" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Service</text>
          <text x="820" y="288" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Audit DB */}
        <g filter="url(#shadow-c4)">
          <ellipse cx="700" cy="340" rx="60" ry="15" fill={styles.database.bg} stroke={styles.database.border} strokeWidth="2"/>
          <rect x="640" y="340" width="120" height="35" fill={styles.database.bg}/>
          <line x1="640" y1="340" x2="640" y2="375" stroke={styles.database.border} strokeWidth="2"/>
          <line x1="760" y1="340" x2="760" y2="375" stroke={styles.database.border} strokeWidth="2"/>
          <ellipse cx="700" cy="375" rx="60" ry="15" fill={styles.database.bg} stroke={styles.database.border} strokeWidth="2"/>
          <text x="700" y="362" textAnchor="middle" className="text-xs font-bold" fill={styles.database.text}>Audit DB</text>
        </g>

        {/* ==================== REPORT ENGINES (RIGHT SIDE) ==================== */}
        
        <rect x="940" y="100" width="260" height="280" rx="8" fill="#f3e8fc" stroke="#7c3aed" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="1070" y="120" textAnchor="middle" className="text-xs font-semibold" fill="#7c3aed">Report Generation Workers</text>

        {/* OBIEE Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="960" y="140" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1010" y="163" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>OBIEE</text>
          <text x="1010" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Worker</text>
        </g>

        {/* Power BI Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="1080" y="140" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1130" y="163" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Power BI</text>
          <text x="1130" y="180" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Worker</text>
        </g>

        {/* MIDAs Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="960" y="210" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1010" y="233" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>MIDAs</text>
          <text x="1010" y="250" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Worker</text>
        </g>

        {/* SSRS Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="1080" y="210" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1130" y="233" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>SSRS</text>
          <text x="1130" y="250" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Worker</text>
        </g>

        {/* Python Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="1020" y="280" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1070" y="303" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Python</text>
          <text x="1070" y="320" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Worker</text>
        </g>

        {/* ==================== S3 EVENT TRIGGER ZONE ==================== */}
        
        <rect x="500" y="420" width="400" height="150" rx="8" fill="#fef3c7" stroke="#d97706" strokeWidth="2" strokeDasharray="5,3"/>
        <text x="700" y="445" textAnchor="middle" className="text-xs font-semibold" fill="#92400e">S3 Event Trigger Zone</text>

        {/* S3 Staging */}
        <g filter="url(#shadow-c4)">
          <rect x="520" y="470" width="130" height="80" rx="6" fill={styles.database.bg} stroke={styles.database.border} strokeWidth="2"/>
          <text x="585" y="500" textAnchor="middle" className="text-xs font-bold" fill={styles.database.text}>☁️ S3 Staging</text>
          <text x="585" y="518" textAnchor="middle" className="text-xs" fill={styles.database.text}>Bucket</text>
          <text x="585" y="538" textAnchor="middle" className="text-xs" fill="#fef3c7">⚡ Event Enabled</text>
        </g>

        {/* EventBridge */}
        <g filter="url(#shadow-c4)">
          <rect x="680" y="470" width="100" height="80" rx="6" fill={styles.event.bg} stroke={styles.event.border} strokeWidth="2"/>
          <text x="730" y="500" textAnchor="middle" className="text-xs font-bold" fill={styles.event.text}>⚡ Event</text>
          <text x="730" y="515" textAnchor="middle" className="text-xs font-bold" fill={styles.event.text}>Bridge</text>
          <text x="730" y="535" textAnchor="middle" className="text-xs" fill={styles.event.text}>[AWS]</text>
        </g>

        {/* Lambda Trigger */}
        <g filter="url(#shadow-c4)">
          <rect x="800" y="470" width="80" height="80" rx="6" fill={styles.event.bg} stroke={styles.event.border} strokeWidth="2"/>
          <text x="840" y="500" textAnchor="middle" className="text-xs font-bold" fill={styles.event.text}>λ Lambda</text>
          <text x="840" y="515" textAnchor="middle" className="text-xs font-bold" fill={styles.event.text}>Trigger</text>
          <text x="840" y="535" textAnchor="middle" className="text-xs" fill={styles.event.text}>[AWS]</text>
        </g>

        {/* ==================== DISTRIBUTION LAYER ==================== */}
        
        <rect x="200" y="600" width="700" height="180" rx="8" fill="#ecfdf5" stroke="#10b981" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="550" y="620" textAnchor="middle" className="text-xs font-semibold" fill="#059669">Distribution Layer</text>

        {/* Distribution Worker */}
        <g filter="url(#shadow-c4)">
          <rect x="220" y="650" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="280" y="675" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Distribution</text>
          <text x="280" y="690" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Worker</text>
          <text x="280" y="708" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Protocol Router */}
        <g filter="url(#shadow-c4)">
          <rect x="360" y="650" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="410" y="675" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Protocol</text>
          <text x="410" y="690" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Router</text>
          <text x="410" y="708" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* FTP Handler */}
        <g filter="url(#shadow-c4)">
          <rect x="480" y="640" width="80" height="50" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="520" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>FTP</text>
          <text x="520" y="677" textAnchor="middle" className="text-xs" fill="#666">Handler</text>
        </g>

        {/* NAS Handler */}
        <g filter="url(#shadow-c4)">
          <rect x="570" y="640" width="80" height="50" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="610" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>NAS</text>
          <text x="610" y="677" textAnchor="middle" className="text-xs" fill="#666">Handler</text>
        </g>

        {/* S3 Handler */}
        <g filter="url(#shadow-c4)">
          <rect x="660" y="640" width="80" height="50" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="700" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>S3</text>
          <text x="700" y="677" textAnchor="middle" className="text-xs" fill="#666">Handler</text>
        </g>

        {/* Email Handler */}
        <g filter="url(#shadow-c4)">
          <rect x="750" y="640" width="80" height="50" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="790" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Email</text>
          <text x="790" y="677" textAnchor="middle" className="text-xs" fill="#666">Handler</text>
        </g>

        {/* Completion Publisher */}
        <g filter="url(#shadow-c4)">
          <rect x="560" y="710" width="130" height="55" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="625" y="733" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Completion</text>
          <text x="625" y="748" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Publisher</text>
        </g>

        {/* ==================== NOTIFICATION LAYER ==================== */}
        
        <rect x="200" y="810" width="500" height="180" rx="8" fill="#fce7f3" stroke="#ec4899" strokeWidth="1.5" strokeDasharray="5,3"/>
        <text x="450" y="830" textAnchor="middle" className="text-xs font-semibold" fill="#be185d">Notification Layer</text>

        {/* Notification Service */}
        <g filter="url(#shadow-c4)">
          <rect x="220" y="860" width="120" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="280" y="885" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Notification</text>
          <text x="280" y="900" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Service</text>
          <text x="280" y="918" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* MQ Publisher */}
        <g filter="url(#shadow-c4)">
          <rect x="360" y="850" width="100" height="55" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="410" y="873" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>MQ</text>
          <text x="410" y="888" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Publisher</text>
        </g>

        {/* Email Notifier */}
        <g filter="url(#shadow-c4)">
          <rect x="360" y="915" width="100" height="55" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="410" y="938" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Email</text>
          <text x="410" y="953" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Notifier</text>
        </g>

        {/* Status Updater */}
        <g filter="url(#shadow-c4)">
          <rect x="480" y="870" width="100" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="530" y="895" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Status</text>
          <text x="530" y="910" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Updater</text>
          <text x="530" y="928" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* Template Engine */}
        <g filter="url(#shadow-c4)">
          <rect x="600" y="870" width="80" height="70" rx="6" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="2"/>
          <text x="640" y="895" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Template</text>
          <text x="640" y="910" textAnchor="middle" className="text-xs font-bold" fill={styles.component.text}>Engine</text>
          <text x="640" y="928" textAnchor="middle" className="text-xs" fill="#666">[Component]</text>
        </g>

        {/* ==================== EXTERNAL TARGETS (RIGHT SIDE) ==================== */}

        {/* External MQ */}
        <g filter="url(#shadow-c4)">
          <rect x="750" y="850" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="800" y="873" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>External</text>
          <text x="800" y="888" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>MQ</text>
        </g>

        {/* User Email */}
        <g filter="url(#shadow-c4)">
          <rect x="750" y="915" width="100" height="55" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="800" y="938" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>User</text>
          <text x="800" y="953" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>Email</text>
        </g>

        {/* ==================== DISTRIBUTION TARGETS (BOTTOM) ==================== */}

        <g filter="url(#shadow-c4)">
          <rect x="940" y="640" width="80" height="50" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="980" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>📁 FTP</text>
          <text x="980" y="677" textAnchor="middle" className="text-xs" fill={styles.external.text}>Server</text>
        </g>

        <g filter="url(#shadow-c4)">
          <rect x="1030" y="640" width="80" height="50" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1070" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>🗄️ NAS</text>
          <text x="1070" y="677" textAnchor="middle" className="text-xs" fill={styles.external.text}>Share</text>
        </g>

        <g filter="url(#shadow-c4)">
          <rect x="1120" y="640" width="80" height="50" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1160" y="662" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>☁️ S3</text>
          <text x="1160" y="677" textAnchor="middle" className="text-xs" fill={styles.external.text}>Target</text>
        </g>

        <g filter="url(#shadow-c4)">
          <rect x="1030" y="700" width="80" height="50" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="1070" y="722" textAnchor="middle" className="text-xs font-bold" fill={styles.external.text}>✉️ Email</text>
          <text x="1070" y="737" textAnchor="middle" className="text-xs" fill={styles.external.text}>Gateway</text>
        </g>

        {/* ==================== ARROWS ==================== */}

        {/* Snowflake -> Poller */}
        <line x1="150" y1="240" x2="215" y2="175" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Poller -> Validator */}
        <line x1="340" y1="175" x2="355" y2="175" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Validator -> Publisher */}
        <line x1="410" y1="210" x2="380" y2="215" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Publisher -> MQ */}
        <line x1="340" y1="290" x2="340" y2="315" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* MQ -> Consumer */}
        <line x1="400" y1="350" x2="515" y2="175" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Consumer -> Orchestrator */}
        <line x1="620" y1="175" x2="635" y2="175" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Orchestrator -> Router */}
        <line x1="760" y1="175" x2="775" y2="175" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Orchestrator -> Status Manager */}
        <line x1="700" y1="210" x2="620" y2="225" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Status Manager -> Audit DB */}
        <line x1="570" y1="300" x2="640" y2="350" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Router -> Workers */}
        <line x1="880" y1="160" x2="955" y2="160" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="880" y1="175" x2="955" y2="237" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Workers -> S3 Staging */}
        <line x1="1070" y1="335" x2="1070" y2="400" stroke="#666" strokeWidth="1.5"/>
        <line x1="1070" y1="400" x2="585" y2="400" stroke="#666" strokeWidth="1.5"/>
        <line x1="585" y1="400" x2="585" y2="465" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* S3 -> EventBridge (Event Flow) */}
        <line x1="650" y1="510" x2="675" y2="510" stroke="#d97706" strokeWidth="2" markerEnd="url(#arrow-event)"/>

        {/* EventBridge -> Lambda */}
        <line x1="780" y1="510" x2="795" y2="510" stroke="#d97706" strokeWidth="2" markerEnd="url(#arrow-event)"/>

        {/* Lambda -> Distribution Worker (Event Flow) */}
        <line x1="840" y1="550" x2="840" y2="590" stroke="#d97706" strokeWidth="2"/>
        <line x1="840" y1="590" x2="280" y2="590" stroke="#d97706" strokeWidth="2"/>
        <line x1="280" y1="590" x2="280" y2="645" stroke="#d97706" strokeWidth="2" markerEnd="url(#arrow-event)"/>

        {/* Distribution Worker -> Protocol Router */}
        <line x1="340" y1="685" x2="355" y2="685" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Protocol Router -> Handlers */}
        <line x1="460" y1="670" x2="475" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="460" y1="685" x2="565" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="460" y1="685" x2="655" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="460" y1="700" x2="745" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Handlers -> External Targets */}
        <line x1="560" y1="665" x2="935" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="650" y1="665" x2="1025" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="740" y1="665" x2="1115" y2="665" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="830" y1="680" x2="1025" y2="725" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Completion Publisher -> Notification */}
        <line x1="625" y1="765" x2="625" y2="790" stroke="#666" strokeWidth="1.5"/>
        <line x1="625" y1="790" x2="280" y2="790" stroke="#666" strokeWidth="1.5"/>
        <line x1="280" y1="790" x2="280" y2="855" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Notification -> Publishers */}
        <line x1="340" y1="895" x2="355" y2="877" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="340" y1="895" x2="355" y2="942" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Publishers -> External */}
        <line x1="460" y1="877" x2="745" y2="877" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>
        <line x1="460" y1="942" x2="745" y2="942" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Status Updater -> Audit DB */}
        <line x1="530" y1="870" x2="530" y2="420" stroke="#666" strokeWidth="1.5"/>
        <line x1="530" y1="420" x2="640" y2="375" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c4)"/>

        {/* Legend */}
        <g transform="translate(950, 820)">
          <rect x="0" y="0" width="250" height="170" rx="6" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1"/>
          <text x="125" y="25" textAnchor="middle" className="text-xs font-bold" fill="#333">Legend</text>
          
          <rect x="15" y="40" width="30" height="20" rx="3" fill={styles.component.bg} stroke={styles.component.border} strokeWidth="1"/>
          <text x="55" y="55" className="text-xs" fill="#666">Internal Component</text>
          
          <rect x="15" y="70" width="30" height="20" rx="3" fill={styles.database.bg} stroke={styles.database.border} strokeWidth="1"/>
          <text x="55" y="85" className="text-xs" fill="#666">Database / Storage</text>
          
          <rect x="15" y="100" width="30" height="20" rx="3" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="1"/>
          <text x="55" y="115" className="text-xs" fill="#666">External System</text>
          
          <rect x="15" y="130" width="30" height="20" rx="3" fill={styles.event.bg} stroke={styles.event.border} strokeWidth="1"/>
          <text x="55" y="145" className="text-xs" fill="#666">Event Trigger (AWS)</text>
        </g>

      </svg>

      {/* Description */}
      <div className="mt-6 max-w-6xl mx-auto">
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-indigo-800 mb-2">About This Diagram</h3>
          <p className="text-xs text-indigo-700">
            The C4 Component Diagram shows the internal structure of the Enterprise Reporting Solution. 
            It details the components within each layer (Ingestion, Orchestration, Distribution, Notification) 
            and their interactions. The S3 Event Trigger Zone highlights the event-driven architecture where 
            file landing triggers automatic distribution via AWS EventBridge and Lambda.
          </p>
        </div>
      </div>
    </div>
  );
};

export default C4ComponentDiagram;
