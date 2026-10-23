// PythonCoin P2P Ad Network - Enhanced Ad Block v2.3.0 (Multi-Type Ad Support)
// Supports: Video ads (.mp4), Picture ads (.jpg/.png), Text ads (.txt), SVG ads (.svg)
// Storage: ads_storage/active folder with automatic ad type detection
// Developer: vike
// PythonCoin Address: 1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi
// Generated: 2026-02-05T19:01:52.554Z
// Zone: main-content
// File: 1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi_adblock.js

(function() {
    "use strict";

    var PYC_AD_CONFIG = {
        zone: "main-content",
        rotation: 30000,
        width: "400px",
        height: "300px",
        developer: "vike",
        pythonCoinAddress: "1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi",
        centralServer: "https://www.secupgrade.com/livepy/pythoncoin/dashboard8.php",
        clients: [{"client_id":"pyc_user_1AGXfryK_e98b99b6","name":"PythonCoin Wallet - user_1AGXfryK","host":"192.168.0.43","port":8082,"status":"online","ad_count":1,"peers":0}],
        currentAdIndex: 0,
        container: null,
        rotationTimer: null,
        totalClicks: 0,
        totalEarned: 0,
        lastError: null,
        registrationAttempts: 0,
        storageAdsLoaded: [],
        lastAdSource: null,
        preferStorageAds: true
    };

    function safeJsonParse(str) {
        try {
            return JSON.parse(str);
        } catch (e) {
            console.error("JSON parse error:", e.message);
            return null;
        }
    }

    function initializeAdBlock() {
        console.log("PythonCoin Enhanced Ad Block v2.3.0 - Storage + Network Support");
        var container = document.querySelector("[data-pyc-zone=\"" + PYC_AD_CONFIG.zone + "\"]");
        if (!container) {
            console.error("PYC Ad Zone not found:", PYC_AD_CONFIG.zone);
            return;
        }
        PYC_AD_CONFIG.container = container;
        setupContainerStyles();
        showPlaceholder("Loading PythonCoin Ads...");
        
        // Load storage ads first, then register with clients
        loadStorageAds();
        registerWithPyQtClients();
        
        if (PYC_AD_CONFIG.rotation > 0) {
            PYC_AD_CONFIG.rotationTimer = setInterval(function() {
                // Alternate between storage and network ads
                if (PYC_AD_CONFIG.lastAdSource === "storage") {
                    loadNextAd();
                } else {
                    displayStorageAd();
                }
            }, PYC_AD_CONFIG.rotation);
        }
    }

    function setupContainerStyles() {
        var container = PYC_AD_CONFIG.container;
        if (!container) return;
        container.style.cssText = "width: " + PYC_AD_CONFIG.width + "; height: " + PYC_AD_CONFIG.height + "; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa; overflow: hidden; position: relative; font-family: Arial, sans-serif; display: flex; align-items: center; justify-content: center;";
    }

    function loadStorageAds() {
        console.log("Loading ads from storage...");
        
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=scan_storage_ads")
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success && data.ads && data.ads.length > 0) {
                    PYC_AD_CONFIG.storageAdsLoaded = data.ads;
                    console.log("Loaded " + data.ads.length + " ads from storage");
                    displayStorageAd();
                } else {
                    console.log("No storage ads found, using network only");
                    setTimeout(loadNextAd, 2000);
                }
            })
            .catch(function(error) {
                console.warn("Storage ads loading failed:", error);
                setTimeout(loadNextAd, 2000);
            });
    }

    function displayStorageAd() {
        if (PYC_AD_CONFIG.storageAdsLoaded.length === 0) {
            loadNextAd();
            return;
        }
        
        var randomAd = PYC_AD_CONFIG.storageAdsLoaded[Math.floor(Math.random() * PYC_AD_CONFIG.storageAdsLoaded.length)];
        PYC_AD_CONFIG.lastAdSource = "storage";
        
        var adType = randomAd.ad_type || "svg";
        console.log("Displaying storage ad (" + adType + "):", randomAd.id);
        
        // Display ad based on type
        switch (adType) {
            case "video":
                displayVideoAd(randomAd, {client_id: "storage"});
                break;
            case "picture":
                displayPictureAd(randomAd, {client_id: "storage"});
                break;
            case "text":
                displayTextAd(randomAd, {client_id: "storage"});
                break;
            case "svg":
            default:
                displaySvgAd(randomAd, {client_id: "storage"});
                break;
        }
    }

    function displayHtmlAd(ad) {
        console.log("Loading HTML ad with enhanced features...");
        
        fetch(ad.html_url)
            .then(function(response) { return response.text(); })
            .then(function(htmlContent) {
                if (htmlContent && htmlContent.includes("<")) {
                    // Create iframe for security and isolation
                    var iframe = document.createElement("iframe");
                    iframe.style.cssText = "width: 100%; height: 100%; border: none; overflow: hidden;";
                    iframe.srcdoc = htmlContent;
                    
                    PYC_AD_CONFIG.container.innerHTML = "";
                    PYC_AD_CONFIG.container.appendChild(iframe);
                    
                    // Add click handler for the entire container
                    PYC_AD_CONFIG.container.style.cursor = "pointer";
                    PYC_AD_CONFIG.container.onclick = function() {
                        // Storage ads get fixed lower payout rate of 0.0000009 PYC
                        var storagePayoutRate = 0.0000009;
                        recordClick(ad.id, "storage", storagePayoutRate);
                        if (ad.target_url || ad.click_url) {
                            window.open(ad.target_url || ad.click_url, "_blank");
                        }
                    };
                    
                    console.log("HTML ad displayed successfully");
                } else {
                    console.warn("Invalid HTML content, falling back to SVG");
                    displaySvgAd(ad, {client_id: "storage"});
                }
            })
            .catch(function(error) {
                console.error("HTML ad loading error:", error);
                displaySvgAd(ad, {client_id: "storage"});
            });
        
        recordView(ad, {client_id: "storage"});
    }

    function registerWithPyQtClients() {
        if (PYC_AD_CONFIG.clients.length === 0) {
            console.log("No P2P clients configured for registration.");
            return;
        }

        PYC_AD_CONFIG.registrationAttempts++;
        console.log("Registration attempt #" + PYC_AD_CONFIG.registrationAttempts + " with configured P2P clients...");

        PYC_AD_CONFIG.clients.forEach(function(client) {
            fetch(PYC_AD_CONFIG.centralServer + "?ajax=proxy_register", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: "client_host=" + encodeURIComponent(client.host) + 
                      "&client_port=" + encodeURIComponent(client.port || "8082") + 
                      "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress) + 
                      "&developer_name=" + encodeURIComponent(PYC_AD_CONFIG.developer) + 
                      "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone)
            })
            .then(function(response) { return response.text(); })
            .then(function(text) {
                var data = safeJsonParse(text);
                if (data && data.success) {
                    console.log("Successfully registered with " + (client.name || client.host));
                } else {
                    console.warn("Failed to register with " + (client.name || client.host));
                }
            })
            .catch(function(e) { 
                console.error("Registration error with " + (client.name || client.host) + ":", e.message); 
            });
        });
    }

    function loadNextAd() {
        if (PYC_AD_CONFIG.clients.length === 0) {
            showFallbackAd("No P2P clients configured");
            return;
        }

        var client = PYC_AD_CONFIG.clients[PYC_AD_CONFIG.currentAdIndex % PYC_AD_CONFIG.clients.length];
        PYC_AD_CONFIG.currentAdIndex++;
        PYC_AD_CONFIG.lastAdSource = "network";
        
        console.log("Loading network ads from:", client.name || client.host);
        console.log("Client host for proxy_ads:", client.host, "Port:", client.port || "8082");
        
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=proxy_ads", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: "client_host=" + encodeURIComponent(client.host) + 
                  "&client_port=" + encodeURIComponent(client.port || "8082") + 
                  "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + 
                  "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress)
        })
        .then(function(response) { return response.text(); })
        .then(function(text) {
            var data = safeJsonParse(text);
            
            if (data && data.success && data.ads && data.ads.length > 0) {
                var randomAd = data.ads[Math.floor(Math.random() * data.ads.length)];
                displaySvgAd(randomAd, client);
            } else {
                console.warn("No network ads available, trying storage fallback");
                if (PYC_AD_CONFIG.storageAdsLoaded.length > 0) {
                    displayStorageAd();
                } else {
                    showFallbackAd("No ads available");
                }
            }
        })
        .catch(function(error) {
            console.error("Network ad loading error:", error);
            if (PYC_AD_CONFIG.storageAdsLoaded.length > 0) {
                displayStorageAd();
            } else {
                showFallbackAd("Network Error");
            }
        });
    }

    function displaySvgAd(ad, client) {
        var svgUrl;
        if (client.client_id === "storage") {
            svgUrl = ad.svg_url;
        } else {
            svgUrl = PYC_AD_CONFIG.centralServer + "?ajax=proxy_svg&client_host=" + encodeURIComponent(client.host || "127.0.0.1") + "&client_port=" + encodeURIComponent(client.port || "8082") + "&ad_id=" + encodeURIComponent(ad.id || ad.ad_id || "unknown");
        }
        
        fetch(svgUrl)
            .then(function(response) { return response.text(); })
            .then(function(svgContent) {
                if (svgContent && (svgContent.includes("<svg") || svgContent.includes("<?xml"))) {
                    PYC_AD_CONFIG.container.innerHTML = svgContent;
                    console.log("SVG ad displayed successfully");
                    addClickHandler(ad, client);
                } else {
                    showFallbackAd("Invalid SVG content");
                }
            })
            .catch(function(error) {
                console.error("SVG loading error:", error);
                showFallbackAd("SVG Load Error");
            });
        
        recordView(ad, client);
    }

    function displayVideoAd(ad, client) {
        console.log("Loading video ad:", ad.id);
        
        var videoUrl;
        if (client.client_id === "storage") {
            videoUrl = ad.video_url;
        } else {
            videoUrl = PYC_AD_CONFIG.centralServer + "?ajax=proxy_video&client_host=" + encodeURIComponent(client.host || "127.0.0.1") + "&client_port=" + encodeURIComponent(client.port || "8082") + "&ad_id=" + encodeURIComponent(ad.id || ad.ad_id || "unknown");
        }
        
        var video = document.createElement("video");
        video.style.cssText = "width: 100%; height: 100%; object-fit: cover;";
        video.src = videoUrl;
        video.autoplay = true;
        video.muted = true;
        video.loop = true;
        video.controls = false;
        
        // Add text overlay if HTML is available
        if (ad.html_url) {
            fetch(ad.html_url)
                .then(function(response) { return response.text(); })
                .then(function(htmlContent) {
                    var overlay = document.createElement("div");
                    overlay.style.cssText = "position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 10;";
                    overlay.innerHTML = htmlContent;
                    
                    PYC_AD_CONFIG.container.innerHTML = "";
                    PYC_AD_CONFIG.container.style.position = "relative";
                    PYC_AD_CONFIG.container.appendChild(video);
                    PYC_AD_CONFIG.container.appendChild(overlay);
                    addClickHandler(ad, client);
                })
                .catch(function(error) {
                    console.warn("Video overlay loading failed:", error);
                    PYC_AD_CONFIG.container.innerHTML = "";
                    PYC_AD_CONFIG.container.appendChild(video);
                    addClickHandler(ad, client);
                });
        } else {
            PYC_AD_CONFIG.container.innerHTML = "";
            PYC_AD_CONFIG.container.appendChild(video);
            addClickHandler(ad, client);
        }
        
        recordView(ad, client);
    }

    function displayPictureAd(ad, client) {
        console.log("Loading picture ad:", ad.id);
        
        var imageUrl;
        if (client.client_id === "storage") {
            imageUrl = ad.image_url;
        } else {
            imageUrl = PYC_AD_CONFIG.centralServer + "?ajax=proxy_image&client_host=" + encodeURIComponent(client.host || "127.0.0.1") + "&client_port=" + encodeURIComponent(client.port || "8082") + "&ad_id=" + encodeURIComponent(ad.id || ad.ad_id || "unknown");
        }
        
        var img = document.createElement("img");
        img.style.cssText = "width: 100%; height: 100%; object-fit: cover;";
        img.src = imageUrl;
        
        img.onload = function() {
            // Add text overlay if HTML is available
            if (ad.html_url) {
                fetch(ad.html_url)
                    .then(function(response) { return response.text(); })
                    .then(function(htmlContent) {
                        var overlay = document.createElement("div");
                        overlay.style.cssText = "position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 10;";
                        overlay.innerHTML = htmlContent;
                        
                        PYC_AD_CONFIG.container.innerHTML = "";
                        PYC_AD_CONFIG.container.style.position = "relative";
                        PYC_AD_CONFIG.container.appendChild(img);
                        PYC_AD_CONFIG.container.appendChild(overlay);
                        addClickHandler(ad, client);
                    })
                    .catch(function(error) {
                        console.warn("Picture overlay loading failed:", error);
                        PYC_AD_CONFIG.container.innerHTML = "";
                        PYC_AD_CONFIG.container.appendChild(img);
                        addClickHandler(ad, client);
                    });
            } else {
                PYC_AD_CONFIG.container.innerHTML = "";
                PYC_AD_CONFIG.container.appendChild(img);
                addClickHandler(ad, client);
            }
        };
        
        img.onerror = function() {
            showFallbackAd("Image Load Error");
        };
        
        recordView(ad, client);
    }

    function displayTextAd(ad, client) {
        console.log("Loading text ad:", ad.id);
        
        var textUrl;
        if (client.client_id === "storage") {
            textUrl = ad.text_url;
        } else {
            textUrl = PYC_AD_CONFIG.centralServer + "?ajax=proxy_text&client_host=" + encodeURIComponent(client.host || "127.0.0.1") + "&client_port=" + encodeURIComponent(client.port || "8082") + "&ad_id=" + encodeURIComponent(ad.id || ad.ad_id || "unknown");
        }
        
        fetch(textUrl)
            .then(function(response) { return response.text(); })
            .then(function(textContent) {
                if (textContent) {
                    if (ad.html_url) {
                        // Use HTML styling if available
                        fetch(ad.html_url)
                            .then(function(response) { return response.text(); })
                            .then(function(htmlContent) {
                                // Replace placeholder in HTML with text content
                                var styledContent = htmlContent.replace(/\{\{text\}\}/g, textContent);
                                var iframe = document.createElement("iframe");
                                iframe.style.cssText = "width: 100%; height: 100%; border: none;";
                                iframe.srcdoc = styledContent;
                                
                                PYC_AD_CONFIG.container.innerHTML = "";
                                PYC_AD_CONFIG.container.appendChild(iframe);
                                addClickHandler(ad, client);
                            })
                            .catch(function(error) {
                                console.warn("Text styling failed:", error);
                                displayPlainTextAd(textContent, ad, client);
                            });
                    } else {
                        displayPlainTextAd(textContent, ad, client);
                    }
                } else {
                    showFallbackAd("Empty Text Content");
                }
            })
            .catch(function(error) {
                console.error("Text loading error:", error);
                showFallbackAd("Text Load Error");
            });
        
        recordView(ad, client);
    }

    function displayPlainTextAd(textContent, ad, client) {
        var textDiv = document.createElement("div");
        textDiv.style.cssText = "padding: 20px; text-align: center; font-family: Arial, sans-serif; font-size: 16px; color: #333; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); height: 100%; box-sizing: border-box; display: flex; align-items: center; justify-content: center;";
        textDiv.textContent = textContent;
        
        PYC_AD_CONFIG.container.innerHTML = "";
        PYC_AD_CONFIG.container.appendChild(textDiv);
        addClickHandler(ad, client);
    }

    function addClickHandler(ad, client) {
        if (!PYC_AD_CONFIG.container) return;
        PYC_AD_CONFIG.container.style.cursor = "pointer";
        PYC_AD_CONFIG.container.onclick = function() {
            // Live ads use negotiated rate (default 0.000005 PYC if not specified)
            var livePayoutRate = ad.payout_amount || ad.payout || 0.000005;
            recordClick(ad.id || ad.ad_id, client.client_id, livePayoutRate);
            if (ad.target_url || ad.click_url) {
                window.open(ad.target_url || ad.click_url, "_blank");
            }
        };
    }

    function showFallbackAd(message) {
        if (!PYC_AD_CONFIG.container) return;
        
        var fallbackSvg = '<svg width="100%" height="100%" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">';
        fallbackSvg += '<defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">';
        fallbackSvg += '<stop offset="0%" style="stop-color:#0066cc;stop-opacity:1" />';
        fallbackSvg += '<stop offset="100%" style="stop-color:#004499;stop-opacity:1" />';
        fallbackSvg += '</linearGradient></defs>';
        fallbackSvg += '<rect width="100%" height="100%" fill="url(#grad1)" rx="10"/>';
        fallbackSvg += '<text x="200" y="120" font-family="Arial" font-size="24" fill="white" text-anchor="middle" font-weight="bold">🌐 PythonCoin</text>';
        fallbackSvg += '<text x="200" y="150" font-family="Arial" font-size="16" fill="white" text-anchor="middle">P2P Ad Network v2.3.0</text>';
        fallbackSvg += '<text x="200" y="180" font-family="Arial" font-size="12" fill="#ccddff" text-anchor="middle">' + (message || "Loading...") + '</text>';
        fallbackSvg += '<text x="200" y="220" font-family="Arial" font-size="10" fill="#ccddff" text-anchor="middle">Storage + Network Integration</text>';
        fallbackSvg += '</svg>';
        
        PYC_AD_CONFIG.container.innerHTML = fallbackSvg;
        PYC_AD_CONFIG.container.style.cursor = "default";
        PYC_AD_CONFIG.container.onclick = null;
    }

    function showPlaceholder(message) {
        if (!PYC_AD_CONFIG.container) return;
        PYC_AD_CONFIG.container.innerHTML = "<div style=\"display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:14px;text-align:center;\">" + message + "</div>";
    }

    function recordView(ad, client) {
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_view", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "ad_id=" + encodeURIComponent(ad.id || ad.ad_id || "unknown") + 
                  "&client_id=" + encodeURIComponent(client.client_id || "unknown") + 
                  "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + 
                  "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress)
        })
        .then(function(response) { 
            if (!response.ok) {
                console.warn("View record failed with status:", response.status);
            }
        })
        .catch(function(e) { 
            console.warn("View record failed:", e.message); 
            // Log to server for debugging purposes
            if (console.debug) console.debug("View record error details:", e);
        });
    }

    function recordClick(adId, clientId, payoutAmount) {
        console.log("Ad clicked:", adId, "Payout:", payoutAmount);
        PYC_AD_CONFIG.totalClicks++;
        PYC_AD_CONFIG.totalEarned += payoutAmount;
        
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_click", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "ad_id=" + encodeURIComponent(adId) + 
                  "&client_id=" + encodeURIComponent(clientId) + 
                  "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + 
                  "&payout_amount=" + encodeURIComponent(payoutAmount) + 
                  "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress)
        })
        .then(function(response) { return response.text(); })
        .then(function(text) {
            var data = safeJsonParse(text);
            if (data && data.success) {
                console.log("Click tracked successfully. Total earned:", PYC_AD_CONFIG.totalEarned.toFixed(8), "PYC");
            } else {
                console.warn("Click tracking failed");
            }
        })
        .catch(function(e) { console.error("Click tracking error:", e.message); });
    }

    // PythonCoin Wallet object for SVG ads compatibility
    window.pythonCoinWallet = {
        recordClick: function(adId) {
            // Find the ad in our loaded ads to get the payout amount and target URL
            var ad = null;
            var client = null;
            
            // Look in storage ads first
            for (var i = 0; i < PYC_AD_CONFIG.storageAdsLoaded.length; i++) {
                if (PYC_AD_CONFIG.storageAdsLoaded[i].id === adId) {
                    ad = PYC_AD_CONFIG.storageAdsLoaded[i];
                    client = {client_id: "storage"};
                    break;
                }
            }
            
            // If not found in storage, try to find in current context
            if (!ad) {
                // Use a default payout rate for storage ads
                ad = {id: adId, target_url: "https://secupgrade.com"};
                client = {client_id: "storage"};
            }
            
            // Use storage ad payout rate (0.0000009) as default
            var payoutRate = 0.0000009;
            
            // If we have ad data, use its payout rate
            if (ad && ad.payout_amount) {
                payoutRate = parseFloat(ad.payout_amount);
            } else if (ad && ad.payout) {
                payoutRate = parseFloat(ad.payout);
            }
            
            // Call the main recordClick function
            recordClick(ad.id, client.client_id, payoutRate);
            
            // Open the target URL if available
            if (ad && (ad.target_url || ad.click_url)) {
                window.open(ad.target_url || ad.click_url, "_blank");
            }
        }
    };

    // Global functions
    window.recordClick = recordClick;

    window.PYC_STATS = function() {
        return {
            totalClicks: PYC_AD_CONFIG.totalClicks,
            totalEarned: PYC_AD_CONFIG.totalEarned,
            developerAddress: PYC_AD_CONFIG.pythonCoinAddress,
            connectedClients: PYC_AD_CONFIG.clients.length,
            storageAdsCount: PYC_AD_CONFIG.storageAdsLoaded.length,
            lastAdSource: PYC_AD_CONFIG.lastAdSource,
            lastError: PYC_AD_CONFIG.lastError,
            version: "2.3.0"
        };
    };

    window.PYC_FORCE_RELOAD = function() {
        console.log("Force reloading ads...");
        if (PYC_AD_CONFIG.storageAdsLoaded.length > 0) {
            displayStorageAd();
        } else {
            loadNextAd();
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeAdBlock);
    } else {
        initializeAdBlock();
    }

})();

/* Enhanced Usage Instructions v2.3.0:
 * 1. Save this file as: 1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi_adblock.js
 * 2. Include in HTML: <script src='1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi_adblock.js'><\/script>
 * 3. Add ad zone: <div data-pyc-zone="main-content"></div>
 * 4. Ads loaded from: ads_storage/active + P2P network
 * 5. HTML ads supported with full interactivity
 * 6. Payments sent to: 1AGXfryKTdEFVT7TQsG8agv4LEX4gnHgSi
 * 7. Debug: console.log(PYC_STATS()) - check version 2.3.0
 * 8. Force reload: PYC_FORCE_RELOAD()
 */