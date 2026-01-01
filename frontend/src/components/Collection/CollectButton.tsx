import React, { useState } from 'react';

interface CollectButtonProps {
  platform: 'reddit' | 'telegram';
  onCollect: (sources: string[], limit: number) => void;
  isCollecting: boolean;
  disabled?: boolean;
}

const defaultSources = {
  // 60 gun TRADE/SALES/WEAPONS related subreddits
  reddit: [
    // Primary Trading/Sales
    'gundeals',              // Gun deals and sales
    'GunAccessoriesForSale', // Accessories trading (GAFS)
    'ComblocMarket',         // AK/Eastern bloc parts
    'GunAccessoryVendors',   // Vendor deals
    'gunsales',              // Gun sales
    'Gunsforsale',           // Gun sales
    'airsoftmarket',         // Airsoft marketplace
    'BrassSwap',             // Ammo trading
    'ReloadingExchange',     // Reloading supplies
    'GunHolsterClassifieds', // Holster trading
    // Knife & Blade Trading
    'Knife_Swap',            // Knife trading
    'KnifeDeals',            // Knife deals
    'BalisongSale',          // Balisong trading
    'EDCexchange',           // EDC gear trading
    // Optics & Accessories
    'opaborat',              // Optics trading
    'GunOptics',             // Optics discussion
    'SuppressedNFA',         // NFA items
    'NFA',                   // NFA items
    'Form1',                 // DIY suppressors
    // Firearms Discussion (potential trade mentions)
    'Firearms',              // General firearms
    'guns',                  // Gun discussion
    'ar15',                  // AR-15 discussion
    'ak47',                  // AK discussion
    'Glocks',                // Glock discussion
    'SigSauer',              // Sig discussion
    'SmithAndWesson',        // S&W discussion
    'CZFirearms',            // CZ discussion
    'Beretta',               // Beretta discussion
    'HecklerKoch',           // HK discussion
    'FNHerstal',             // FN discussion
    'Ruger',                 // Ruger discussion
    'Remington',             // Remington discussion
    'Mossberg',              // Mossberg discussion
    'Shotguns',              // Shotguns
    'Revolvers',             // Revolvers
    '1911',                  // 1911 pistols
    'longrange',             // Long range rifles
    'PlebeianAR',            // AR builds
    'ar15build',             // AR builds
    'GunPorn',               // Gun photos
    'Handguns',              // Handguns
    'CCW',                   // Concealed carry
    'EDC',                   // Everyday carry
    'tacticalgear',          // Tactical gear
    'QualityTacticalGear',   // Tactical gear
    // Military & Surplus
    'MilitaryCollecting',    // Military collectibles
    'milsurp',               // Military surplus
    'SKS',                   // SKS rifles
    'Mauser',                // Mauser rifles
    'MosinNagant',           // Mosin rifles
    // Ammo & Reloading
    'ammo',                  // Ammunition
    'reloading',             // Reloading
    'InStockAmmo',           // Ammo in stock alerts
    // Legal/Gray Area Discussions
    'liberalgunowners',      // Gun owners
    'SocialistRA',           // Gun owners
    'progun',                // Pro-gun
    'Firearms_Advice',       // Firearms advice
    'GunMemes',              // Gun culture
    'ForgottenWeapons',      // Historic weapons
  ],
  telegram: [
    'warmonitors',        // Conflict monitoring
    'militaborat',        // Military operations
    'ryaborig',           // Defense news (RU)
    'militaryarmament',   // Military equipment
    'ArmyRecognition',    // Defense industry
    'defence_blog',       // Military tech
    'conflictnews',       // Global conflicts
    'warfakes',           // Conflict fact-check
    'militaryweapons',    // Weapons systems
  ],
};

const CollectButton: React.FC<CollectButtonProps> = ({
  platform,
  onCollect,
  isCollecting,
  disabled = false,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [sources, setSources] = useState<string[]>(defaultSources[platform]);
  const [sourcesInput, setSourcesInput] = useState(defaultSources[platform].join(', '));
  const [limit, setLimit] = useState(5); // Default to 5 for faster collection with AI

  const handleSubmit = () => {
    const sourceList = sourcesInput
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    if (sourceList.length > 0) {
      onCollect(sourceList, limit);
      setShowModal(false);
    }
  };

  const icon = platform === 'reddit' ? '🔴' : '✈️';
  const label = platform === 'reddit' ? 'Reddit' : 'Telegram';
  const color = platform === 'reddit' ? '#ff4500' : '#0088cc';

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        disabled={isCollecting || disabled}
        style={{
          ...styles.button,
          background: isCollecting
            ? 'rgba(255,170,0,0.2)'
            : `linear-gradient(90deg, ${color}, ${color}88)`,
          borderColor: isCollecting ? '#ffaa00' : color,
          opacity: disabled ? 0.5 : 1,
          cursor: disabled ? 'not-allowed' : 'pointer',
        }}
      >
        <span>{isCollecting ? '⏳' : icon}</span>
        {isCollecting ? 'COLLECTING...' : `COLLECT FROM ${label.toUpperCase()}`}
      </button>

      {/* Collection Config Modal */}
      {showModal && (
        <div style={styles.overlay} onClick={() => setShowModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>
              {icon} Configure {label} Collection
            </h3>

            <div style={styles.field}>
              <label style={styles.label}>
                {platform === 'reddit' ? 'Subreddits' : 'Channels/Groups'}
              </label>
              <textarea
                value={sourcesInput}
                onChange={(e) => setSourcesInput(e.target.value)}
                placeholder={platform === 'reddit' 
                  ? 'news, worldnews, technology, firearms'
                  : '@channel1, @channel2'}
                style={styles.textarea}
                rows={3}
              />
              <span style={styles.hint}>Separate multiple entries with commas</span>
            </div>

            <div style={styles.field}>
              <label style={styles.label}>
                Limit per {platform === 'reddit' ? 'subreddit' : 'channel'}
              </label>
              <input
                type="number"
                value={limit}
                onChange={(e) => setLimit(Math.min(50, Math.max(1, parseInt(e.target.value) || 1)))}
                min={1}
                max={50}
                style={styles.input}
              />
            </div>

            <div style={styles.actions}>
              <button
                onClick={() => setShowModal(false)}
                style={styles.cancelButton}
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                style={{
                  ...styles.submitButton,
                  background: `linear-gradient(90deg, ${color}, ${color}88)`,
                }}
              >
                Start Collection
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  button: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '14px 24px',
    border: '1px solid',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 700,
    color: '#fff',
    letterSpacing: '1px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  overlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    width: '100%',
    maxWidth: '450px',
    background: 'linear-gradient(135deg, #001a2e 0%, #000a14 100%)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '15px',
    padding: '30px',
  },
  modalTitle: {
    margin: '0 0 25px 0',
    fontSize: '18px',
    color: '#00ffff',
    fontWeight: 600,
  },
  field: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    fontSize: '12px',
    color: '#888',
    letterSpacing: '1px',
    marginBottom: '8px',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#fff',
    fontFamily: 'inherit',
    resize: 'vertical' as const,
  },
  input: {
    width: '100px',
    padding: '12px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#fff',
    fontFamily: 'inherit',
  },
  hint: {
    display: 'block',
    fontSize: '11px',
    color: '#666',
    marginTop: '5px',
  },
  actions: {
    display: 'flex',
    gap: '15px',
    marginTop: '25px',
  },
  cancelButton: {
    flex: 1,
    padding: '12px',
    background: 'transparent',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#888',
    cursor: 'pointer',
  },
  submitButton: {
    flex: 1,
    padding: '12px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 700,
    color: '#fff',
    cursor: 'pointer',
  },
};

export default CollectButton;

