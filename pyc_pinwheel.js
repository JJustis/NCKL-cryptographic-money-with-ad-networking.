/*! PythonCoin Pinwheel transparent encryption (ratchet adapted from pinwheel-freechat).
 *  Drop-in:  pycPinwheel.fetch(url, init)  works like fetch() but the request and response bodies are
 *  AES-256-GCM ciphertext on the wire. No accounts: the session opens automatically and lives in memory only.
 *    handshake : random 32-byte root, sent inside an ECDH(P-256)+HKDF+AES-GCM envelope to the server key
 *    per query : epoch_key = HKDF(root,"epoch-E"), msg_key = HKDF(epoch_key,"msg-N"), E = 20 s epochs, N unique */
(function (root) {
  var enc = new TextEncoder(), dec = new TextDecoder(), subtle = crypto.subtle;
  function b64(buf) { var s = "", b = new Uint8Array(buf); for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); return btoa(s); }
  function unb64(s) { var r = atob(s), b = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) b[i] = r.charCodeAt(i); return b; }
  function rid(n) { var a = new Uint8Array(n); crypto.getRandomValues(a); return b64(a).replace(/[+\/=]/g, "A").slice(0, 24).padEnd(16, "A"); }
  function cat(a, b) { var o = new Uint8Array(a.length + b.length); o.set(a, 0); o.set(b, a.length); return o; }

  function hkdf(ikmBytes, info) {
    return subtle.importKey("raw", ikmBytes, "HKDF", false, ["deriveBits"]).then(function (k) {
      return subtle.deriveBits({ name: "HKDF", hash: "SHA-256", salt: new Uint8Array(0), info: enc.encode(info) }, k, 256);
    }).then(function (bits) { return new Uint8Array(bits); });
  }
  function aesKey(raw, usage) { return subtle.importKey("raw", raw, "AES-GCM", false, [usage]); }
  function seal(raw, plainBytes, aad) {
    var iv = crypto.getRandomValues(new Uint8Array(12));
    return aesKey(raw, "encrypt").then(function (k) {
      return subtle.encrypt({ name: "AES-GCM", iv: iv, additionalData: enc.encode(aad), tagLength: 128 }, k, plainBytes);
    }).then(function (ct) { return cat(iv, new Uint8Array(ct)); });
  }
  function open(raw, blob, aad) {
    return aesKey(raw, "decrypt").then(function (k) {
      return subtle.decrypt({ name: "AES-GCM", iv: blob.slice(0, 12), additionalData: enc.encode(aad), tagLength: 128 }, k, blob.slice(12));
    }).then(function (p) { return new Uint8Array(p); });
  }

  // ---- session handshake (one per server directory) -------------------------------------------------------
  var sessions = {};
  function baseOf(url) { var u = new URL(url, location.href); return u.origin + u.pathname.replace(/[^\/]*$/, ""); }

  function openSession(base) {
    var apiUrl = base + "api.php";
    return fetch(apiUrl, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "public_key" }) })
      .then(function (r) { return r.json(); })
      .then(function (j) { return subtle.importKey("raw", unb64(j.public_key), { name: "ECDH", namedCurve: "P-256" }, false, []); })
      .then(function (srvPub) {
        var rootBytes = crypto.getRandomValues(new Uint8Array(32));
        return subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]).then(function (eph) {
          return Promise.all([subtle.exportKey("raw", eph.publicKey), subtle.deriveBits({ name: "ECDH", public: srvPub }, eph.privateKey, 256)]);
        }).then(function (r) {
          return hkdf(new Uint8Array(r[1]), "pyc-report-v1").then(function (k) {
            var body = { action: "pw_open", root: b64(rootBytes), ts: Math.floor(Date.now() / 1000), nonce: rid(24) };
            var iv = crypto.getRandomValues(new Uint8Array(12));           // envelope: iv, then ciphertext||tag
            return aesKey(k, "encrypt").then(function (ak) {
              return subtle.encrypt({ name: "AES-GCM", iv: iv, tagLength: 128 }, ak, enc.encode(JSON.stringify(body)));
            }).then(function (ct) { return { enc: { v: 1, epk: b64(r[0]), iv: b64(iv), ct: b64(ct) } }; });
          });
        }).then(function (envelope) {
          var t0 = Date.now();
          return fetch(apiUrl, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(envelope) }).then(function (resp) {
            return resp.json().then(function (j) {
              if (!j.pw) throw new Error("pinwheel: handshake refused");
              return hkdf(rootBytes, "pw-open").then(function (ok) { return open(ok, unb64(j.ct), "pw-open"); }).then(function (p) {
                var info = JSON.parse(dec.decode(p));
                return { sid: info.sid, root: rootBytes, start: info.start, eps: info.epoch_seconds, offset: info.server_time - Math.floor((t0 + Date.now()) / 2000), counters: {} };
              });
            });
          });
        });
      });
  }
  function session(base, force) {
    if (force || !sessions[base]) sessions[base] = openSession(base).catch(function (e) { delete sessions[base]; throw e; });
    return sessions[base];
  }

  // ---- one encrypted query --------------------------------------------------------------------------------
  function query(url, init, retry) {
    var base = baseOf(url);
    return session(base, false).then(function (s) {
      var E = Math.floor((Date.now() / 1000 + s.offset - s.start) / s.eps);
      var N = s.counters[E] = (s.counters[E] || 0); s.counters[E]++;          // synchronous: unique even when parallel
      var aad = s.sid + "|" + E + "|" + N;
      var bodyText = typeof init.body === "string" ? init.body : "{}";
      var u = new URL(url, location.href);
      var payload = {}; try { payload = JSON.parse(bodyText); } catch (e) { payload = Object.fromEntries(new URLSearchParams(bodyText)); }
      u.searchParams.forEach(function (v, k) { if (!(k in payload)) payload[k] = v; });  // ?action=... travels inside the ciphertext
      u.search = "";
      return hkdf(s.root, "epoch-" + E).then(function (ek) { return hkdf(ek, "msg-" + N); }).then(function (mk) {
        return seal(mk, enc.encode(JSON.stringify(payload)), aad).then(function (blob) {
          return hkdf(mk, "resp").then(function (rk) {
            return fetch(u.toString(), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pw: { v: 1, sid: s.sid, e: E, n: N, ct: b64(blob) } }) })
              .then(function (resp) {
                return resp.text().then(function (txt) {
                  var j = null; try { j = JSON.parse(txt); } catch (e) {}
                  if (j && j.pw) return open(rk, unb64(j.ct), aad + "|r").then(function (p) { return new Response(dec.decode(p), { status: resp.status, headers: { "Content-Type": "application/json" } }); });
                  if (!retry && resp.status === 400) { return session(base, true).then(function () { return query(url, init, true); }); }  // expired session
                  return new Response(txt, { status: resp.status, headers: resp.headers });
                });
              });
          });
        });
      });
    });
  }

  root.pycPinwheel = { fetch: function (url, init) { return query(url, init || {}, false); } };
})(typeof window !== "undefined" ? window : globalThis);
