import React from 'react';

const C2ContextDiagram = () => {
  const styles = {
    person: { bg: '#08427b', border: '#073b6f', text: '#ffffff' },
    system: { bg: '#1168bd', border: '#0e5ca3', text: '#ffffff' },
    external: { bg: '#999999', border: '#7a7a7a', text: '#ffffff' },
    boundary: { bg: '#ffffff', border: '#cccccc', text: '#666666' },
  };

  return (
    <div className="p-8 bg-white min-h-screen">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Enterprise Reporting Solution</h1>
        <h2 className="text-lg text-blue-600 mt-1">System Context Diagram (C2)</h2>
        <p className="text-sm text-gray-500 mt-2">Level 2: Shows the system in context with users and external systems</p>
      </div>

      <svg viewBox="0 0 1200 800" className="w-full max-w-6xl mx-auto">
        <defs>
          <marker id="arrow-c2" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#666666" />
          </marker>
          <filter id="shadow-c2" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="2" dy="3" stdDeviation="3" floodOpacity="0.2"/>
          </filter>
        </defs>

        {/* Title */}
        <text x="600" y="30" textAnchor="middle" className="text-sm font-bold" fill="#333">
          [System Context] Enterprise Reporting Solution
        </text>

        {/* ==================== ACTORS (TOP) ==================== */}
        
        {/* Business User */}
        <g filter="url(#shadow-c2)">
          <circle cx="150" cy="120" r="35" fill={styles.person.bg} stroke={styles.person.border} strokeWidth="2"/>
          <text x="150" y="115" textAnchor="middle" className="text-xs font-bold" fill={styles.person.text}>👤</text>
          <text x="150" y="130" textAnchor="middle" className="text-xs" fill={styles.person.text}>User</text>
        </g>
        <text x="150" y="170" textAnchor="middle" className="text-xs font-semibold" fill="#333">Business User</text>
        <text x="150" y="185" textAnchor="middle" className="text-xs" fill="#666">[Person]</text>
        <text x="150" y="200" textAnchor="middle" className="text-xs" fill="#666">Submits report requests</text>
        <text x="150" y="213" textAnchor="middle" className="text-xs" fill="#666">and receives outputs</text>

        {/* Operations Team */}
        <g filter="url(#shadow-c2)">
          <circle cx="400" cy="120" r="35" fill={styles.person.bg} stroke={styles.person.border} strokeWidth="2"/>
          <text x="400" y="115" textAnchor="middle" className="text-xs font-bold" fill={styles.person.text}>👤</text>
          <text x="400" y="130" textAnchor="middle" className="text-xs" fill={styles.person.text}>Ops</text>
        </g>
        <text x="400" y="170" textAnchor="middle" className="text-xs font-semibold" fill="#333">Operations Team</text>
        <text x="400" y="185" textAnchor="middle" className="text-xs" fill="#666">[Person]</text>
        <text x="400" y="200" textAnchor="middle" className="text-xs" fill="#666">Monitors workflows,</text>
        <text x="400" y="213" textAnchor="middle" className="text-xs" fill="#666">handles failures</text>

        {/* Downstream Systems */}
        <g filter="url(#shadow-c2)">
          <circle cx="650" cy="120" r="35" fill={styles.person.bg} stroke={styles.person.border} strokeWidth="2"/>
          <text x="650" y="115" textAnchor="middle" className="text-xs font-bold" fill={styles.person.text}>🖥️</text>
          <text x="650" y="130" textAnchor="middle" className="text-xs" fill={styles.person.text}>Sys</text>
        </g>
        <text x="650" y="170" textAnchor="middle" className="text-xs font-semibold" fill="#333">Downstream Systems</text>
        <text x="650" y="185" textAnchor="middle" className="text-xs" fill="#666">[External System]</text>
        <text x="650" y="200" textAnchor="middle" className="text-xs" fill="#666">Consumes report</text>
        <text x="650" y="213" textAnchor="middle" className="text-xs" fill="#666">completion events</text>

        {/* External Partners */}
        <g filter="url(#shadow-c2)">
          <circle cx="900" cy="120" r="35" fill={styles.person.bg} stroke={styles.person.border} strokeWidth="2"/>
          <text x="900" y="115" textAnchor="middle" className="text-xs font-bold" fill={styles.person.text}>🏢</text>
          <text x="900" y="130" textAnchor="middle" className="text-xs" fill={styles.person.text}>Partner</text>
        </g>
        <text x="900" y="170" textAnchor="middle" className="text-xs font-semibold" fill="#333">External Partners</text>
        <text x="900" y="185" textAnchor="middle" className="text-xs" fill="#666">[Person/System]</text>
        <text x="900" y="200" textAnchor="middle" className="text-xs" fill="#666">Receives reports via</text>
        <text x="900" y="213" textAnchor="middle" className="text-xs" fill="#666">FTP/Email</text>

        {/* ==================== MAIN SYSTEM (CENTER) ==================== */}
        
        <g filter="url(#shadow-c2)">
          <rect x="350" y="300" width="300" height="180" rx="8" fill={styles.system.bg} stroke={styles.system.border} strokeWidth="3"/>
          <text x="500" y="340" textAnchor="middle" className="text-base font-bold" fill={styles.system.text}>Enterprise Reporting</text>
          <text x="500" y="360" textAnchor="middle" className="text-base font-bold" fill={styles.system.text}>Solution</text>
          <text x="500" y="385" textAnchor="middle" className="text-xs" fill={styles.system.text}>[Software System]</text>
          <text x="500" y="410" textAnchor="middle" className="text-xs" fill={styles.system.text}>Orchestrates report generation</text>
          <text x="500" y="425" textAnchor="middle" className="text-xs" fill={styles.system.text}>across multiple engines and</text>
          <text x="500" y="440" textAnchor="middle" className="text-xs" fill={styles.system.text}>distributes to various destinations</text>
          <text x="500" y="455" textAnchor="middle" className="text-xs" fill={styles.system.text}>with full audit trail</text>
        </g>

        {/* ==================== EXTERNAL SYSTEMS (BOTTOM & SIDES) ==================== */}

        {/* Snowflake */}
        <g filter="url(#shadow-c2)">
          <rect x="50" y="350" width="160" height="100" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="130" y="385" textAnchor="middle" className="text-sm font-bold" fill={styles.external.text}>Snowflake</text>
          <text x="130" y="405" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External System]</text>
          <text x="130" y="425" textAnchor="middle" className="text-xs" fill={styles.external.text}>Data Warehouse</text>
          <text x="130" y="440" textAnchor="middle" className="text-xs" fill={styles.external.text}>& Request Queue</text>
        </g>

        {/* Report Engines */}
        <g filter="url(#shadow-c2)">
          <rect x="790" y="350" width="160" height="100" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="870" y="385" textAnchor="middle" className="text-sm font-bold" fill={styles.external.text}>Report Engines</text>
          <text x="870" y="405" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External Systems]</text>
          <text x="870" y="425" textAnchor="middle" className="text-xs" fill={styles.external.text}>OBIEE, Power BI,</text>
          <text x="870" y="440" textAnchor="middle" className="text-xs" fill={styles.external.text}>MIDAs, SSRS</text>
        </g>

        {/* AWS Services */}
        <g filter="url(#shadow-c2)">
          <rect x="200" y="550" width="160" height="100" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="280" y="585" textAnchor="middle" className="text-sm font-bold" fill={styles.external.text}>AWS Services</text>
          <text x="280" y="605" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External System]</text>
          <text x="280" y="625" textAnchor="middle" className="text-xs" fill={styles.external.text}>S3, EventBridge,</text>
          <text x="280" y="640" textAnchor="middle" className="text-xs" fill={styles.external.text}>Lambda, SQS, SES</text>
        </g>

        {/* Distribution Targets */}
        <g filter="url(#shadow-c2)">
          <rect x="440" y="550" width="160" height="100" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="520" y="585" textAnchor="middle" className="text-sm font-bold" fill={styles.external.text}>Distribution Targets</text>
          <text x="520" y="605" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External Systems]</text>
          <text x="520" y="625" textAnchor="middle" className="text-xs" fill={styles.external.text}>FTP, NAS, S3,</text>
          <text x="520" y="640" textAnchor="middle" className="text-xs" fill={styles.external.text}>Email Gateway</text>
        </g>

        {/* Message Queue */}
        <g filter="url(#shadow-c2)">
          <rect x="680" y="550" width="160" height="100" rx="6" fill={styles.external.bg} stroke={styles.external.border} strokeWidth="2"/>
          <text x="760" y="585" textAnchor="middle" className="text-sm font-bold" fill={styles.external.text}>Message Queue</text>
          <text x="760" y="605" textAnchor="middle" className="text-xs" fill={styles.external.text}>[External System]</text>
          <text x="760" y="625" textAnchor="middle" className="text-xs" fill={styles.external.text}>Kafka / SQS</text>
          <text x="760" y="640" textAnchor="middle" className="text-xs" fill={styles.external.text}>Event Bus</text>
        </g>

        {/* ==================== RELATIONSHIP ARROWS ==================== */}

        {/* Business User -> System */}
        <line x1="150" y1="155" x2="150" y2="260" stroke="#666" strokeWidth="1.5"/>
        <line x1="150" y1="260" x2="350" y2="350" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="160" y="250" width="120" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="220" y="262" textAnchor="middle" className="text-xs" fill="#666">Submits requests,</text>
        <text x="220" y="274" textAnchor="middle" className="text-xs" fill="#666">views status</text>

        {/* Operations -> System */}
        <line x1="400" y1="155" x2="400" y2="260" stroke="#666" strokeWidth="1.5"/>
        <line x1="400" y1="260" x2="450" y2="295" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="405" y="235" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="450" y="247" textAnchor="middle" className="text-xs" fill="#666">Monitors,</text>
        <text x="450" y="259" textAnchor="middle" className="text-xs" fill="#666">troubleshoots</text>

        {/* System -> Downstream */}
        <line x1="550" y1="295" x2="550" y2="260" stroke="#666" strokeWidth="1.5"/>
        <line x1="550" y1="260" x2="650" y2="160" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="555" y="200" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="600" y="212" textAnchor="middle" className="text-xs" fill="#666">Sends events</text>
        <text x="600" y="224" textAnchor="middle" className="text-xs" fill="#666">via MQ</text>

        {/* System -> Partners */}
        <line x1="650" y1="350" x2="750" y2="250" stroke="#666" strokeWidth="1.5"/>
        <line x1="750" y1="250" x2="900" y2="160" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="755" y="200" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="800" y="212" textAnchor="middle" className="text-xs" fill="#666">Delivers reports</text>
        <text x="800" y="224" textAnchor="middle" className="text-xs" fill="#666">FTP/Email</text>

        {/* Snowflake <-> System */}
        <line x1="210" y1="400" x2="345" y2="400" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <line x1="345" y1="380" x2="210" y2="380" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="230" y="350" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="275" y="362" textAnchor="middle" className="text-xs" fill="#666">Reads requests,</text>
        <text x="275" y="374" textAnchor="middle" className="text-xs" fill="#666">writes status</text>

        {/* System -> Report Engines */}
        <line x1="655" y1="400" x2="785" y2="400" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="670" y="370" width="100" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="720" y="382" textAnchor="middle" className="text-xs" fill="#666">Generates reports</text>
        <text x="720" y="394" textAnchor="middle" className="text-xs" fill="#666">via API calls</text>

        {/* System <-> AWS */}
        <line x1="400" y1="485" x2="320" y2="545" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="300" y="500" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="345" y="512" textAnchor="middle" className="text-xs" fill="#666">Uses S3, events,</text>
        <text x="345" y="524" textAnchor="middle" className="text-xs" fill="#666">compute</text>

        {/* System -> Distribution */}
        <line x1="500" y1="485" x2="500" y2="545" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="505" y="500" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="550" y="512" textAnchor="middle" className="text-xs" fill="#666">Distributes to</text>
        <text x="550" y="524" textAnchor="middle" className="text-xs" fill="#666">targets</text>

        {/* System <-> MQ */}
        <line x1="600" y1="485" x2="720" y2="545" stroke="#666" strokeWidth="1.5" markerEnd="url(#arrow-c2)"/>
        <rect x="620" y="500" width="90" height="30" rx="3" fill="white" stroke="#ddd" strokeWidth="1"/>
        <text x="665" y="512" textAnchor="middle" className="text-xs" fill="#666">Publishes events,</text>
        <text x="665" y="524" textAnchor="middle" className="text-xs" fill="#666">consumes jobs</text>

        {/* Legend */}
        <g transform="translate(920, 550)">
          <text x="0" y="0" className="text-xs font-bold" fill="#333">Legend</text>
          <circle cx="15" cy="25" r="12" fill={styles.person.bg}/>
          <text x="35" y="30" className="text-xs" fill="#666">Person</text>
          <rect x="3" y="45" width="24" height="16" rx="3" fill={styles.system.bg}/>
          <text x="35" y="58" className="text-xs" fill="#666">System (Internal)</text>
          <rect x="3" y="70" width="24" height="16" rx="3" fill={styles.external.bg}/>
          <text x="35" y="83" className="text-xs" fill="#666">External System</text>
        </g>

      </svg>

      {/* Description */}
      <div className="mt-8 max-w-4xl mx-auto">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">About This Diagram</h3>
          <p className="text-xs text-blue-700">
            The C2 Context Diagram shows the Enterprise Reporting Solution in its operational context. 
            It identifies the key actors (Business Users, Operations Team, External Partners) and the 
            external systems it integrates with (Snowflake, Report Engines, AWS Services, Distribution Targets, Message Queue).
            This view helps stakeholders understand the system boundaries and integration points.
          </p>
        </div>
      </div>
    </div>
  );
};

export default C2ContextDiagram;
