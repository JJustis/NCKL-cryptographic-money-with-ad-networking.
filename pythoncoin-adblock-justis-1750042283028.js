// PythonCoin P2P Ad Network - Generated Ad Block
// Developer: justis
// PythonCoin Address: 1CZSeEzAyKcbR9fytcT1hTKnG7PpcBhXoi
// Generated: 2025-06-16T02:51:21.212Z
// Zone: main-content

(function() {
    "use strict";

    var PYC_AD_CONFIG = {
        zone: "main-content",
        rotation: 30000,
        width: "400px",
        height: "300px",
        developer: "justis",
        pythonCoinAddress: "1CZSeEzAyKcbR9fytcT1hTKnG7PpcBhXoi",
        centralServer: "https://secupgrade.com/livepy/pythoncoin/dashboard.php",
        clients: [{"client_id":"0e880e87","name":"PythonCoin Wallet - 1CZSeEzA...","host":"192.168.0.58","port":"8082","status":"online","ad_count":"0","peers":0}],
        currentAdIndex: 0,
        container: null,
        rotationTimer: null
    };

    function initializeAdBlock() {
        console.log("PythonCoin Ad Block Initializing...", PYC_AD_CONFIG);
        var container = document.querySelector("[data-pyc-zone=\"" + PYC_AD_CONFIG.zone + "\"]");
        if (!container) {
            console.error("PYC Ad Zone not found:", PYC_AD_CONFIG.zone);
            return;
        }
        PYC_AD_CONFIG.container = container;
        container.style.width = PYC_AD_CONFIG.width;
        container.style.height = PYC_AD_CONFIG.height;
        container.style.border = "1px solid #ddd";
        container.style.borderRadius = "8px";
        container.style.backgroundColor = "#f8f9fa";
        loadNextAd();
        if (PYC_AD_CONFIG.rotation > 0) {
            PYC_AD_CONFIG.rotationTimer = setInterval(loadNextAd, PYC_AD_CONFIG.rotation);
        }
    }

    function loadNextAd() {
        if (PYC_AD_CONFIG.clients.length === 0) {
            showPlaceholder("No P2P clients connected");
            return;
        }
        var client = PYC_AD_CONFIG.clients[PYC_AD_CONFIG.currentAdIndex % PYC_AD_CONFIG.clients.length];
        PYC_AD_CONFIG.currentAdIndex++;
        fetch("http://" + client.host + ":" + client.port + "/ads?zone=" + PYC_AD_CONFIG.zone)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.ads && data.ads.length > 0) {
                    displayAd(data.ads[0], client);
                } else {
                    showPlaceholder("No ads from " + client.name);
                }
            })
            .catch(function() {
                showPlaceholder("Loading ads...");
            });
    }

    function displayAd(ad, client) {
        var html = "<div style=\"padding:15px;height:100%;display:flex;flex-direction:column;justify-content:center;\">";
        html += "<h4 style=\"margin:0 0 8px 0;font-size:14px;text-align:center;\">" + ad.title + "</h4>";
        html += "<p style=\"margin:0 0 10px 0;font-size:12px;color:#666;text-align:center;\">" + ad.description + "</p>";
        html += "<div style=\"text-align:center;\"><button onclick=\"recordClick(\'" + ad.id + "\', \'" + client.client_id + "\')\" style=\"background:#0066cc;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;\">Learn More</button></div>";
        html += "</div>";
        PYC_AD_CONFIG.container.innerHTML = html;
    }

    function showPlaceholder(message) {
        PYC_AD_CONFIG.container.innerHTML = "<div style=\"display:flex;align-items:center;justify-content:center;height:100%;color:#666;\">" + message + "</div>";
    }

    window.recordClick = function(adId, clientId) {
        console.log("Ad clicked:", adId);
        fetch(PYC_AD_CONFIG.centralServer + "?ajax=record_click", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: "ad_id=" + encodeURIComponent(adId) + "&client_id=" + encodeURIComponent(clientId) + "&zone=" + encodeURIComponent(PYC_AD_CONFIG.zone) + "&payout_amount=0.001"
        }).then(function(response) { return response.json(); })
          .then(function(data) {
              if (data.success) {
                  console.log("Click recorded successfully");
              }
          })
          .catch(function(e) { console.error("Click record failed:", e); });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeAdBlock);
    } else {
        initializeAdBlock();
    }
})();

