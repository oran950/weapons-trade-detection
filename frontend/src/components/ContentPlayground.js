import React, { useState } from 'react';

const ContentPlayground = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  
  // Form state
  const [contentType, setContentType] = useState('post');
  const [intensityLevel, setIntensityLevel] = useState('low');
  const [quantity, setQuantity] = useState(5);
  const [includeContact, setIncludeContact] = useState(false);
  const [includePricing, setIncludePricing] = useState(false);

  const generateContent = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:9000/api/generation/content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content_type: contentType,
          intensity_level: intensityLevel,
          quantity: parseInt(quantity),
          include_contact: includeContact,
          include_pricing: includePricing
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setGeneratedContent(data.content);
        setAnalysisResults([]); // Clear previous analysis
      }
    } catch (error) {
      console.error('Generation failed:', error);
      alert('Content generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateBatch = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:9000/api/generation/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quantity_per_type: 3,
          include_contact: includeContact,
          include_pricing: includePricing
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        // Flatten all intensity levels into one array
        const allContent = [
          ...data.batch_results.low_intensity,
          ...data.batch_results.medium_intensity,
          ...data.batch_results.high_intensity
        ];
        setGeneratedContent(allContent);
        setAnalysisResults([]);
      }
    } catch (error) {
      console.error('Batch generation failed:', error);
      alert('Batch generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const analyzeContent = async (content) => {
    try {
      const response = await fetch('http://localhost:9000/api/detection/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content.content
        })
      });

      const analysisData = await response.json();
      
      // Update analysis results
      setAnalysisResults(prev => [...prev, {
        contentId: content.id,
        analysis: analysisData
      }]);
      
      return analysisData;
    } catch (error) {
      console.error('Analysis failed:', error);
      return null;
    }
  };

  const getAnalysisForContent = (contentId) => {
    return analysisResults.find(result => result.contentId === contentId)?.analysis;
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH': return '#dc2626'; // red
      case 'MEDIUM': return '#f59e0b'; // yellow
      case 'LOW': return '#16a34a'; // green
      default: return '#6b7280'; // gray
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ color: '#333', marginBottom: '30px' }}>
        Content Generation Playground
      </h2>
      
      <div style={{ 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffeaa7', 
        borderRadius: '8px', 
        padding: '15px', 
        marginBottom: '30px' 
      }}>
        <strong>Academic Research Only:</strong> This tool generates synthetic content for testing detection algorithms in controlled academic environments.
      </div>

      {/* Generation Controls */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '20px', 
        marginBottom: '30px',
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px'
      }}>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Content Type:
          </label>
          <select 
            value={contentType} 
            onChange={(e) => setContentType(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="post">Social Media Post</option>
            <option value="message">Direct Message</option>
            <option value="ad">Classified Ad</option>
            <option value="forum">Forum Discussion</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Intensity Level:
          </label>
          <select 
            value={intensityLevel} 
            onChange={(e) => setIntensityLevel(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="low">Low (Sporting Goods)</option>
            <option value="medium">Medium (Tactical Gear)</option>
            <option value="high">High (Direct References)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Quantity:
          </label>
          <input 
            type="number" 
            min="1" 
            max="20" 
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input 
              type="checkbox" 
              checked={includeContact}
              onChange={(e) => setIncludeContact(e.target.checked)}
            />
            Include Contact Info
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input 
              type="checkbox" 
              checked={includePricing}
              onChange={(e) => setIncludePricing(e.target.checked)}
            />
            Include Pricing
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
        <button 
          onClick={generateContent}
          disabled={isGenerating}
          style={{
            padding: '12px 24px',
            backgroundColor: isGenerating ? '#6b7280' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isGenerating ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {isGenerating ? 'Generating...' : 'Generate Content'}
        </button>

        <button 
          onClick={generateBatch}
          disabled={isGenerating}
          style={{
            padding: '12px 24px',
            backgroundColor: isGenerating ? '#6b7280' : '#059669',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isGenerating ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          Generate Batch (All Types)
        </button>
      </div>

      {/* Generated Content Display */}
      {generatedContent.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '20px' }}>Generated Content ({generatedContent.length} items)</h3>
          
          <div style={{ display: 'grid', gap: '20px' }}>
            {generatedContent.map((content, index) => {
              const analysis = getAnalysisForContent(content.id);
              
              return (
                <div 
                  key={content.id}
                  style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '20px',
                    backgroundColor: '#ffffff'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
                    <div>
                      <span style={{ 
                        backgroundColor: '#e5e7eb', 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        marginRight: '10px',
                        color: '#374151',
                        fontWeight: '600'
                      }}>
                        {content.parameters.type.toUpperCase()}
                      </span>
                      <span style={{ 
                        backgroundColor: content.parameters.intensity === 'high' ? '#fee2e2' : 
                                       content.parameters.intensity === 'medium' ? '#fef3c7' : '#dcfce7',
                        color: content.parameters.intensity === 'high' ? '#991b1b' : 
                               content.parameters.intensity === 'medium' ? '#92400e' : '#166534',
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        fontWeight: '600'
                      }}>
                        {content.parameters.intensity.toUpperCase()}
                      </span>
                    </div>
                    
                    <button
                      onClick={() => analyzeContent(content)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#6366f1',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Analyze
                    </button>
                  </div>

                  <div style={{ 
                    backgroundColor: '#f9fafb', 
                    padding: '15px', 
                    borderRadius: '6px', 
                    marginBottom: '15px',
                    fontFamily: 'monospace',
                    fontSize: '14px',
                    lineHeight: '1.5',
                    color: '#1f2937',
                    border: '1px solid #e5e7eb'
                  }}>
                    {content.content}
                  </div>

                  {analysis && (
                    <div style={{
                      backgroundColor: analysis.risk_level === 'HIGH' ? '#fef2f2' :
                                     analysis.risk_level === 'MEDIUM' ? '#fefbf2' : '#f0fdf4',
                      border: `1px solid ${getRiskLevelColor(analysis.risk_level)}`,
                      borderRadius: '6px',
                      padding: '15px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '10px' }}>
                        <span style={{ 
                          color: getRiskLevelColor(analysis.risk_level), 
                          fontWeight: 'bold' 
                        }}>
                          Risk Level: {analysis.risk_level}
                        </span>
                        <span style={{ color: '#6b7280' }}>
                          Score: {Math.round(analysis.risk_score * 100)}%
                        </span>
                        <span style={{ color: '#6b7280' }}>
                          Confidence: {Math.round(analysis.confidence * 100)}%
                        </span>
                      </div>
                      
                      {analysis.flags && analysis.flags.length > 0 && (
                        <div>
                          <strong>Detected Issues:</strong>
                          <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                            {analysis.flags.map((flag, i) => (
                              <li key={i} style={{ fontSize: '13px', marginBottom: '3px' }}>
                                {flag}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  <div style={{ 
                    marginTop: '15px', 
                    fontSize: '12px', 
                    color: '#374151',
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '10px',
                    fontWeight: '500'
                  }}>
                    <div><strong>Platform:</strong> {content.metadata.platform}</div>
                    <div><strong>Location:</strong> {content.metadata.location}</div>
                    <div><strong>ID:</strong> {content.id}</div>
                    <div><strong>Generated:</strong> {new Date(content.generated_at).toLocaleString()}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Summary Statistics */}
      {generatedContent.length > 0 && (
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '8px' 
        }}>
          <h4 style={{ marginBottom: '15px' }}>Generation Summary</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <strong>Total Generated:</strong> {generatedContent.length}
            </div>
            <div>
              <strong>Analyzed:</strong> {analysisResults.length}
            </div>
            <div>
              <strong>High Risk:</strong> {analysisResults.filter(r => r.analysis.risk_level === 'HIGH').length}
            </div>
            <div>
              <strong>Medium Risk:</strong> {analysisResults.filter(r => r.analysis.risk_level === 'MEDIUM').length}
            </div>
            <div>
              <strong>Low Risk:</strong> {analysisResults.filter(r => r.analysis.risk_level === 'LOW').length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentPlayground;