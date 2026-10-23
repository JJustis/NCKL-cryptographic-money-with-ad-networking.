// PythonCoin P2P Ad Network - Enhanced Ad Block (CORS Proxy Version)
// Developer: justis
// PythonCoin Address: 1CZSeEzAyKcbR9fytcT1hTKnG7PpcBhXoi
// Generated: 2025-06-16T16:57:46.461Z
// Zone: main-content
// ** This file name must include developer address: 1CZSeEzA_adblock.js **

(function() {
    "use strict";

    var PYC_AD_CONFIG = {
        zone: "main-content",
        rotation: 30000,
        width: "400px",
        height: "300px",
        developer: "justis",
        pythonCoinAddress: "1CZSeEzAyKcbR9fytcT1hTKnG7PpcBhXoi",
        centralServer: "https://secupgrade.com/livepy/pythoncoin/dashboard7.php",
        clients: [{"client_id":"5a27e30d","name":"PythonCoin Wallet - 1CZSeEzA...","host":"localhost","port":"8082","status":"online","ad_count":"1","peers":0}],
        currentAdIndex: 0,
        container: null,
        rotationTimer: null,
        totalClicks: 0,
        totalEarned: 0
    };

    function initializeAdBlock() {
        console.log("PythonCoin Enhanced Ad Block Initializing (CORS Proxy)...", PYC_AD_CONFIG);
        var container = document.querySelector("[data-pyc-zone=\"" + PYC_AD_CONFIG.zone + "\"]");
        if (!container) {
            console.error("PYC Ad Zone not found:", PYC_AD_CONFIG.zone);
            return;
        }
        PYC_AD_CONFIG.container = container;
        setupContainerStyles();
        registerWithPyQtClients();
        loadNextAd();
        if (PYC_AD_CONFIG.rotation > 0) {
            PYC_AD_CONFIG.rotationTimer = setInterval(loadNextAd, PYC_AD_CONFIG.rotation);
        }
    }

    function setupContainerStyles() {
        var container = PYC_AD_CONFIG.container;
        if (!container) return;
        container.style.cssText = "width: " + PYC_AD_CONFIG.width + "; height: " + PYC_AD_CONFIG.height + "; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa; overflow: hidden; position: relative; font-family: Arial, sans-serif;";
    }

    function registerWithPyQtClients() {
        for (var i = 0; i < PYC_AD_CONFIG.clients.length; i++) {
            var client = PYC_AD_CONFIG.clients[i];
            
            fetch(PYC_AD_CONFIG.centralServer + "?ajax=proxy_register", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: "client_host=" + encodeURIComponent(client.host) + 
                      "&client_port=" + encodeURIComponent(client.port || "8082") + 
                      "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress) + 
                      "&developer_name=" + encodeURIComponent(PYC_AD_CONFIG.developer) + 
                      "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    console.log("Registered with PyQt client via proxy:", data);
                } else {
                    console.log("PyQt registration failed:", data.error);
                }
            })
            .catch(function(e) { console.log("PyQt client registration failed:", e); });
        }
    }

    function loadNextAd() {
        if (PYC_AD_CONFIG.clients.length === 0) {
            showPlaceholder("No P2P clients connected");
            return;
        }
        var client = PYC_AD_CONFIG.clients[PYC_AD_CONFIG.currentAdIndex % PYC_AD_CONFIG.clients.length];
        PYC_AD_CONFIG.currentAdIndex++;
        
        console.log("Loading ads via proxy from:", client.name);
        
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=proxy_ads", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: "client_host=" + encodeURIComponent(client.host) + 
                  "&client_port=" + encodeURIComponent(client.port || "8082") + 
                  "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + 
                  "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress)
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            console.log("Proxy ads response:", data);
            if (data.ads && data.ads.length > 0) {
                displaySvgAd(data.ads[0], client);
            } else if (data.success === false) {
                showPlaceholder("Proxy Error: " + (data.error || "Unknown"));
            } else {
                showPlaceholder("No ads from " + client.name);
            }
        })
        .catch(function(error) {
            console.error("Ad loading error:", error);
            showPlaceholder("Loading ads...");
        });
    }

    function displaySvgAd(ad, client) {
        var svgProxyUrl = PYC_AD_CONFIG.centralServer + "?ajax=proxy_svg";
        var formData = "client_host=" + encodeURIComponent(client.host) + 
                      "&client_port=" + encodeURIComponent(client.port || "8082") + 
                      "&ad_id=" + encodeURIComponent(ad.id);
        
        console.log("Loading SVG via proxy for ad:", ad.id);
        
        fetch(svgProxyUrl, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        })
        .then(function(response) { return response.text(); })
        .then(function(svgContent) {
            if (svgContent.startsWith("<svg") || svgContent.includes("svg")) {
                PYC_AD_CONFIG.container.innerHTML = svgContent;
                console.log("SVG ad displayed successfully");
            } else {
                console.log("Invalid SVG response:", svgContent);
                showPlaceholder("SVG Load Error");
            }
        })
        .catch(function(error) {
            console.error("SVG loading error:", error);
            showPlaceholder("SVG Load Failed");
        });
        
        // Record view
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_view", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "ad_id=" + encodeURIComponent(ad.id) + "&client_id=" + encodeURIComponent(client.client_id) + "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + "&developer_address=" + encodeURIComponent(PYC_AD_CONFIG.pythonCoinAddress)
        }).catch(function(e) { console.log("View record failed:", e); });
    }

    function showPlaceholder(message) {
        if (!PYC_AD_CONFIG.container) return;
        PYC_AD_CONFIG.container.innerHTML = "<div style=\"display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:14px;\">" + message + "</div>";
    }

    window.recordClick = function(adId, clientId, payoutAmount) {
        console.log("Ad interaction tracked:", adId, "Payout:", payoutAmount);
        PYC_AD_CONFIG.totalClicks++;
        PYC_AD_CONFIG.totalEarned += payoutAmount;
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_click", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "ad_id=" + encodeURIComponent(adId) + "&client_id=" + encodeURIComponent(clientId) + "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + "&payout_amount=" + payoutAmount
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success) {
                console.log("Click tracked successfully. Total earned:", PYC_AD_CONFIG.totalEarned.toFixed(8), "PYC");
            }
        })
        .catch(function(e) { console.error("Click tracking failed:", e); });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeAdBlock);
    } else {
        initializeAdBlock();
    }

    window.PYC_STATS = function() {
        return {
            totalClicks: PYC_AD_CONFIG.totalClicks,
            totalEarned: PYC_AD_CONFIG.totalEarned,
            developerAddress: PYC_AD_CONFIG.pythonCoinAddress,
            connectedClients: PYC_AD_CONFIG.clients.length
        };
    };

})();

/* Usage Instructions:
 * 1. Save this file as: 1CZSeEzA_adblock.js
 * 2. Include in your HTML: <script src='1CZSeEzA_adblock.js'><\/script>
 * 3. Add ad zone to your page: <div data-pyc-zone="main-content"></div>
 * 4. Payments will be sent to: 1CZSeEzAyKcbR9fytcT1hTKnG7PpcBhXoi
 * 5. All P2P requests are proxied through: https://secupgrade.com/livepy/pythoncoin/dashboard7.php
 */