// Progressive enhancement only: the site works fully without this file.
(function () {
  "use strict";
  // "Copy" buttons on code blocks
  document.querySelectorAll("pre.code").forEach(function (pre) {
    if (!navigator.clipboard) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      var text = pre.innerText.replace(/\n?Copy$/, "").trim();
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = "Copy"; }, 1600);
      }, function () { btn.textContent = "Press Ctrl+C"; });
    });
    pre.appendChild(btn);
  });
  // close the mobile menu after choosing a link
  var toggle = document.getElementById("navtoggle");
  if (toggle) document.querySelectorAll(".nav a").forEach(function (a) {
    a.addEventListener("click", function () { toggle.checked = false; });
  });
})();
