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

  // Big data generation state
  const [bigDataQuantity, setBigDataQuantity] = useState(2000);
  const [selectedPlatforms, setSelectedPlatforms] = useState(['reddit', 'twitter', 'facebook', 'instagram']);
  const [selectedLengths, setSelectedLengths] = useState(['short', 'medium', 'long']);

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
      window.alert('Content generation failed');
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
      window.alert('Batch generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateBigData = async () => {
    if (!window.confirm(`This will generate ${bigDataQuantity} posts. This may take a while. Continue?`)) {
      return;
    }
    
    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:9000/api/generation/big-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_quantity: parseInt(bigDataQuantity),
          platforms: selectedPlatforms,
          content_lengths: selectedLengths
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setGeneratedContent(data.content);
        setAnalysisResults([]);
        window.alert(`Successfully generated ${data.statistics.total_generated} posts!`);
      }
    } catch (error) {
      console.error('Big data generation failed:', error);
      window.alert('Big data generation failed: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev => 
      prev.includes(platform) 
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  const toggleLength = (length) => {
    setSelectedLengths(prev => 
      prev.includes(length) 
        ? prev.filter(l => l !== length)
        : [...prev, length]
    );
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

  const downloadJSON = () => {
    if (generatedContent.length === 0) {
      window.alert('No content to download');
      return;
    }

    const dataToDownload = {
      generated_at: new Date().toISOString(),
      total_items: generatedContent.length,
      content: generatedContent,
      analysis_results: analysisResults,
      summary: {
        total_generated: generatedContent.length,
        analyzed: analysisResults.length,
        high_risk: analysisResults.filter(r => r.analysis.risk_level === 'HIGH').length,
        medium_risk: analysisResults.filter(r => r.analysis.risk_level === 'MEDIUM').length,
        low_risk: analysisResults.filter(r => r.analysis.risk_level === 'LOW').length
      }
    };

    const jsonString = JSON.stringify(dataToDownload, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `generated_content_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ color: '#333', marginBottom: '30px' }}>
        Content Generation Playground
      </h2>
      

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

      {/* Big Data Generation Section */}
      <div style={{
        marginTop: '40px',
        padding: '25px',
        backgroundColor: '#f0f9ff',
        borderRadius: '8px',
        border: '2px solid #3b82f6'
      }}>
        <h3 style={{ color: '#1e40af', marginBottom: '20px' }}>
          🚀 Big Data Generation (2000+ Posts)
        </h3>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px',
          marginBottom: '20px'
        }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Total Quantity:
            </label>
            <input 
              type="number" 
              min="100" 
              max="10000" 
              value={bigDataQuantity}
              onChange={(e) => setBigDataQuantity(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
            Platforms:
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['reddit', 'twitter', 'facebook', 'instagram'].map(platform => (
              <label key={platform} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '5px',
                padding: '8px 12px',
                backgroundColor: selectedPlatforms.includes(platform) ? '#3b82f6' : '#e5e7eb',
                color: selectedPlatforms.includes(platform) ? 'white' : '#374151',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}>
                <input 
                  type="checkbox" 
                  checked={selectedPlatforms.includes(platform)}
                  onChange={() => togglePlatform(platform)}
                  style={{ cursor: 'pointer' }}
                />
                {platform.charAt(0).toUpperCase() + platform.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
            Content Lengths:
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['short', 'medium', 'long'].map(length => (
              <label key={length} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '5px',
                padding: '8px 12px',
                backgroundColor: selectedLengths.includes(length) ? '#059669' : '#e5e7eb',
                color: selectedLengths.includes(length) ? 'white' : '#374151',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500'
              }}>
                <input 
                  type="checkbox" 
                  checked={selectedLengths.includes(length)}
                  onChange={() => toggleLength(length)}
                  style={{ cursor: 'pointer' }}
                />
                {length.charAt(0).toUpperCase() + length.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <button 
          onClick={generateBigData}
          disabled={isGenerating || selectedPlatforms.length === 0 || selectedLengths.length === 0}
          style={{
            padding: '14px 28px',
            backgroundColor: isGenerating || selectedPlatforms.length === 0 || selectedLengths.length === 0 
              ? '#6b7280' : '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isGenerating || selectedPlatforms.length === 0 || selectedLengths.length === 0 
              ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            width: '100%'
          }}
        >
          {isGenerating ? `Generating ${bigDataQuantity} posts...` : `Generate ${bigDataQuantity} Posts for Big Data Analysis`}
        </button>
      </div>

      {/* Generated Content Display */}
      {generatedContent.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ margin: 0 }}>Generated Content ({generatedContent.length} items)</h3>
            <button
              onClick={downloadJSON}
              style={{
                padding: '10px 20px',
                backgroundColor: '#8b5cf6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span>⬇</span> Download JSON
            </button>
          </div>
          
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