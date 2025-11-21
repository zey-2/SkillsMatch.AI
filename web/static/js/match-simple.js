// Simplified Job Matching JavaScript
// This replaces the complex logic with a cleaner, more reliable approach

// Global flags to prevent double calls
window.matchingStates = {};

// Simple, reliable matching function - expose to global scope
window.performSimpleMatching = function performSimpleMatching(profileId) {
    console.log('🚀 Starting simple matching for profile:', profileId);
    
    // Preemptively reset any animation states that might cause issues
    const preContainer = document.getElementById('resultsContainer');
    const preResultsSection = document.getElementById('matchingResults');
    if (preContainer) {
        preContainer.style.opacity = '1';
        preContainer.style.transform = 'none';
        preContainer.style.animation = 'none';
        preContainer.style.visibility = 'visible';
        preContainer.classList.remove('animate__animated', 'animate__fadeInUp');
    }
    if (preResultsSection) {
        preResultsSection.style.opacity = '1';
        preResultsSection.style.transform = 'none';
        preResultsSection.style.animation = 'none';
        preResultsSection.style.visibility = 'visible';
    }
    console.log('🎭 Preemptive animation state reset completed');
    
    // Reset any previous animation states
    const container = document.getElementById('resultsContainer');
    if (container) {
        container.style.opacity = '1';
        container.style.transform = 'none';
        container.style.animation = 'none';
    }
    
    // ENHANCED duplicate call prevention with timestamp
    const now = Date.now();
    const matchKey = `matching_${profileId}`;
    const lastCallKey = `lastCall_${profileId}`;
    
    // Check if already running
    if (window[matchKey] === true) {
        console.log('⚠️ Already matching for this profile, skipping');
        return;
    }
    
    // Check if called too recently (within 2 seconds)
    if (window[lastCallKey] && (now - window[lastCallKey]) < 2000) {
        console.log('⚠️ Called too recently, preventing duplicate');
        return;
    }
    
    // Set multiple flags with timestamp
    window[matchKey] = true;
    window[lastCallKey] = now;
    window.matchingStates = window.matchingStates || {};
    window.matchingStates[profileId] = true;
    
    console.log('✅ Match call approved for profile:', profileId);
    
    // Show progress
    const progressSection = document.getElementById('matchingProgress');
    const resultsSection = document.getElementById('matchingResults');
    
    if (progressSection) progressSection.style.display = 'block';
    if (resultsSection) resultsSection.style.display = 'none';
    
    updateProgress(20, 'Starting job search...');
    
    // Make API call with small delay to prevent race conditions
    setTimeout(() => {
        fetch('/api/match-efficient', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_id: profileId, limit: 10 })
        })
        .then(response => {
            updateProgress(60, 'Processing matches...');
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateProgress(100, 'Complete!');
            displaySimpleResults(data);
        })
        .catch(error => {
            console.error('❌ Matching error:', error);
            showError('Matching failed: ' + error.message);
        })
        .finally(() => {
            // Always reset ALL flags with delay to prevent rapid re-calls
            setTimeout(() => {
                const matchKey = `matching_${profileId}`;
                window[matchKey] = false;
                if (window.matchingStates) {
                    window.matchingStates[profileId] = false;
                }
                console.log('🔄 Flags reset for profile:', profileId);
            }, 500);
            
            setTimeout(() => {
                if (progressSection) progressSection.style.display = 'none';
            }, 1000);
        });
    }, 100); // Small delay to prevent race conditions
}

// Simple results display - expose to global scope with display state management
window.displaySimpleResults = function displaySimpleResults(data) {
    console.log('📊 Displaying results:', data);
    console.log('🔍 Data validation - matches array:', data.matches ? data.matches.length : 'undefined');
    console.log('🔍 Data validation - profile_name:', data.profile_name);
    
    // Prevent display corruption on multiple calls
    if (window.displayInProgress) {
        console.log('⚠️ Display already in progress, skipping');
        return;
    }
    window.displayInProgress = true;
    console.log('✅ Display state set to in progress');
    
    const container = document.getElementById('resultsContainer');
    const resultsSection = document.getElementById('matchingResults');
    const headerInfo = document.getElementById('matchResultsHeader');
    
    if (!container) {
        console.error('❌ Container not found');
        return;
    }
    
    console.log('🔍 Container found, current content length:', container.innerHTML.length);
    
    // Show results section and reset CSS state
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.style.opacity = '1';
        resultsSection.style.transform = 'none';
        resultsSection.style.animation = 'none';
        console.log('✅ Results section shown and CSS reset');
    }
    
    // Reset container CSS state to prevent animation issues
    container.style.opacity = '1';
    container.style.transform = 'none';
    container.style.animation = 'none';
    container.style.visibility = 'visible';
    container.classList.remove('animate__animated', 'animate__fadeInUp');
    console.log('✅ Container CSS state reset and animation classes removed');
    
    // Update header
    if (headerInfo && data.profile_name) {
        headerInfo.innerHTML = `
            <h5 class="mb-0"><i class="fas fa-chart-line me-2"></i>Matches for ${data.profile_name}</h5>
            <small class="text-muted">Found ${data.matches?.length || 0} opportunities</small>
        `;
    }
    
    // Handle no matches
    if (!data.matches || data.matches.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No matches found</h5>
                <p class="text-muted">Try adjusting your profile or search again later.</p>
                <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
            </div>
        `;
        return;
    }
    
    // Generate cards with validation
    let html = '<div class="row g-3">';
    console.log('🔍 Building HTML for', data.matches.length, 'matches');
    
    if (!Array.isArray(data.matches)) {
        console.error('❌ Matches data is not an array:', typeof data.matches);
        container.innerHTML = '<div class="alert alert-danger">Invalid match data received</div>';
        return;
    }
    
    data.matches.slice(0, 6).forEach((match, index) => {
        const score = Math.round(match.match_percentage || 85);
        const badgeClass = score >= 80 ? 'success' : score >= 60 ? 'warning' : 'info';
        
        // Enhanced text cleaning function to remove HTML and clean text
        const cleanText = (text, maxLen = 100) => {
            if (!text) return '';
            let cleaned = String(text);
            
            // Remove HTML tags completely
            cleaned = cleaned.replace(/<[^>]*>/g, ' ');
            
            // Remove HTML entities
            cleaned = cleaned.replace(/&[a-zA-Z0-9#]+;/g, ' ');
            
            // Remove extra whitespace and special characters
            cleaned = cleaned.replace(/\s+/g, ' ');
            cleaned = cleaned.replace(/[<>&"'`]/g, '');
            
            // Trim and limit length
            cleaned = cleaned.trim().slice(0, maxLen);
            
            // Ensure it ends properly
            if (cleaned.length === maxLen) {
                cleaned = cleaned.substring(0, cleaned.lastIndexOf(' '));
            }
            
            return cleaned || 'Job opportunity available';
        };
        
        const title = cleanText(match.job_title || 'Job Opportunity', 50);
        const company = cleanText(match.company_name || 'Company', 40);
        const location = cleanText(match.location || 'Singapore', 30);
        const desc = cleanText(match.job_description || 'Great opportunity matching your skills.', 120);
        
        html += `
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card h-100 shadow-sm" style="border-radius: 12px; opacity: 1; transform: none; animation: none !important;">
                    <div class="card-header bg-light" style="border-radius: 12px 12px 0 0;">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1 pe-2">
                                <h6 class="mb-1 fw-bold text-truncate">${title}</h6>
                                <small class="text-muted text-truncate d-block">${company}</small>
                            </div>
                            <span class="badge bg-${badgeClass} fs-6">${score}%</span>
                        </div>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <div class="mb-3">
                            <small class="text-muted d-flex align-items-center mb-1">
                                <i class="fas fa-map-marker-alt me-1"></i>${location}
                            </small>
                            <small class="text-muted d-flex align-items-center">
                                <i class="fas fa-briefcase me-1"></i>Full-time
                            </small>
                        </div>
                        <p class="text-muted small flex-grow-1" style="line-height: 1.4;">
                            ${desc}...
                        </p>
                        <div class="d-flex gap-2 mt-auto">
                            <button class="btn btn-sm btn-outline-primary flex-fill" onclick="viewJob('${match.job_id || index}')">
                                <i class="fas fa-eye me-1"></i>View
                            </button>
                            <button class="btn btn-sm btn-primary flex-fill">
                                <i class="fas fa-paper-plane me-1"></i>Apply
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    console.log('🔍 Final HTML length:', html.length);
    console.log('🔍 HTML preview:', html.substring(0, 200) + '...');
    
    // Set the HTML
    container.innerHTML = html;
    console.log('✅ HTML content set in container');
    
    // Force CSS reset on all cards to prevent animation state issues (including slideInUp)
    setTimeout(() => {
        const jobCards = container.querySelectorAll('.card');
        jobCards.forEach((card) => {
            card.style.opacity = '1';
            card.style.transform = 'none';
            card.style.animation = 'none';
            card.style.visibility = 'visible';
            // Remove any slideInUp or animate.css classes
            card.classList.remove('animate__slideInUp', 'animate__animated', 'slide-up');
        });
        console.log('🎭 CSS reset and slideInUp removal applied to', jobCards.length, 'job cards');
    }, 100);
    
    console.log('✅ Results displayed successfully');
    
    // Reset display flag after successful display
    setTimeout(() => {
        window.displayInProgress = false;
        console.log('🔄 Display flag reset');
    }, 1000);
}

// Progress update function
function updateProgress(percent, message) {
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
    }
    
    if (progressStatus) {
        progressStatus.innerHTML = `<small class="text-muted">${message}</small>`;
    }
}

// Error display function
function showError(message) {
    const container = document.getElementById('resultsContainer');
    const resultsSection = document.getElementById('matchingResults');
    
    if (resultsSection) resultsSection.style.display = 'block';
    
    if (container) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <h5>Error</h5>
                <p class="text-muted">${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
            </div>
        `;
    }
}

console.log('✅ Simple matching JavaScript loaded');