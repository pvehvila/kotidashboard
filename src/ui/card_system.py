# src/ui/card_system.py
from __future__ import annotations

from datetime import datetime

import streamlit as st
from streamlit.components.v1 import html as st_html

from src.config import TZ
from src.utils import get_ip
from src.ui.common import section_title

# ------------------- SYSTEM STATUS CARD -------------------


def card_system() -> None:
    """Render a system status card incl. device/browser info (no debug box, no UA dump)."""
    try:
        section_title("🖥️ Järjestelmätila", mt=10, mb=4)

        ip_addr = get_ip()
        now_str = datetime.now(TZ).strftime("%H:%M:%S")

        html = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  :root {{
    --fg:#e7eaee;
    --bg:rgba(255,255,255,0.04);
    --bd:rgba(255,255,255,0.08);
    --fg-hint:rgba(231,234,238,0.8);
  }}
  html,body {{ margin:0; padding:0; background:transparent; color:var(--fg);
               font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu; }}
  .card {{ position:relative; overflow:hidden; border-radius:14px; background:var(--bg); border:1px solid var(--bd); }}
  .card-body {{ padding:8px 12px 10px 12px; }}
  .grid {{ display:grid; grid-template-columns:auto 1fr; gap:4px 10px; align-items:center;
           font-size:.92rem; line-height:1.25; }}
  .hint {{ color:var(--fg-hint); }}
  .muted {{ opacity:.7; font-size:.85rem; padding-top:2px; }}
</style>
</head><body>
  <section class="card">
    <div class="card-body">
      <div class="grid" style="margin-bottom:4px;">
        <div class="hint">IP:</div><div>{ip_addr}</div>
        <div class="hint">Päivitetty:</div><div>{now_str}</div>
        <div class="hint">Kioskitila:</div><div>Fully Kiosk Browser</div>
      </div>

      <div id="device-info" class="grid muted" style="margin-top:6px;">
        <div class="muted">Kerätään laitteen tietoja…</div><div></div>
      </div>
    </div>
  </section>

<script>
window.addEventListener('DOMContentLoaded', function () {{
  var target = document.getElementById('device-info');

  function show(rows) {{
    var html = "";
    for (var i=0;i<rows.length;i++) {{
      html += "<div class='hint'>" + rows[i][0] + ":</div><div>" + rows[i][1] + "</div>";
    }}
    target.innerHTML = html;
  }}

  try {{
    var ua = navigator.userAgent || "";
    var vw = Math.round(window.innerWidth || 0);
    var vh = Math.round(window.innerHeight || 0);
    var sw = (screen && screen.width) ? screen.width : 0;
    var sh = (screen && screen.height) ? screen.height : 0;

    function detectOS() {{
      if (ua.indexOf("Windows NT") > -1) {{
        var m = /Windows NT (\\d+\\.\\d+)/.exec(ua);
        var name = "Windows";
        if (m && m[1] && m[1].indexOf("10.0") === 0) {{
          var v = (/Edg\\/(\\d+)/.exec(ua) || /Chrome\\/(\\d+)/.exec(ua) || [,"0"])[1];
          name = (parseInt(v,10) >= 95) ? "Windows 11" : "Windows 10";
        }}
        var is64 = /Win64|x64|WOW64/i.test(ua);
        return name + " " + (is64 ? "(64-bit)" : "(32-bit)");
      }}
      if (/CrOS/i.test(ua)) return "ChromeOS";
      if (/iPhone|iPod/i.test(ua)) return "iOS";
      if (/iPad/i.test(ua) || (ua.indexOf("Macintosh")>-1 && 'ontouchend' in document)) return "iPadOS";
      if (/Android/i.test(ua)) return "Android";
      if (/Mac OS X|Macintosh/i.test(ua)) return "macOS";
      if (/Linux/i.test(ua)) return "Linux";
      return navigator.platform || "Tuntematon";
    }}

    var isPhone = /(Mobile|Android.*Mobile|Phone)/i.test(ua);
    var isTV = /(SmartTV|TV|BRAVIA|AFT[BMT]|AppleTV|Tizen|Web0S)/i.test(ua);
    var deviceType = isTV ? "TV" : (isPhone ? "Puhelin" : "Tietokone");

    var b = (/(Edg|OPR|Chrome|Firefox|Safari)/i.exec(ua) || ["","Tuntematon"])[1];
    if (b === "OPR") b = "Opera";
    if (b === "Edg") b = "Edge";

    var osLabel = detectOS();

    var rows = [
      ["Laitetyyppi", deviceType],
      ["Käyttöjärjestelmä", osLabel],
      ["Selain", b],
      ["Viewport", vw + "×" + vh],
      ["Resoluutio", sw + "×" + sh]
    ];
    show(rows);
  }} catch (err) {{
    target.innerHTML = "<div class='hint'>Virhe:</div><div>" + (err && err.message ? err.message : String(err)) + "</div>";
  }}
}});
</script>
</body></html>
"""
        st_html(html, height=200, scrolling=False)

    except Exception as e:
        section_title("🖥️ Järjestelmätila")
        st.markdown(f"<span class='hint'>Virhe: {e}</span>", unsafe_allow_html=True)
