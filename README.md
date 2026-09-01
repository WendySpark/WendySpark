<div align="center">

# WendySpark

<img src="./stats.svg" width="620" alt="Contributions in the last year"/>

</div>

<img src="./hd-about.svg" width="620" alt="about"/>

> Life's short. Take the risk, do the work.

<img src="./hd-stack.svg" width="620" alt="stack"/>

<samp>python &nbsp; c++ &nbsp; java &nbsp; dart &nbsp; pytorch &nbsp; scikit-learn &nbsp; flutter &nbsp; firebase &nbsp; git</samp>

<img src="./hd-projects.svg" width="620" alt="projects"/>

**[AI-Enhanced Phishing Detection](https://github.com/WendySpark/ai-enhanced-phishing-detection)** &nbsp;·&nbsp; <samp>python, pytorch, flask</samp><br>
Hybrid BERT + CNN + Bi-LSTM + XGBoost model for detecting phishing emails,<br>
evaluated on held-out cross-corpus data. Ships with a Flask web app and SHAP explainability.

**[Mobile Tow Booking System](https://github.com/WendySpark/mobile-tow-booking-system)** &nbsp;·&nbsp; <samp>flutter, firebase, dart</samp><br>
Role-based tow-booking prototype (Admin, User, Insurance Agent, Workshop) with<br>
real-time driver tracking, payment gating, and admin analytics.

**[AES Encryption](https://github.com/WendySpark/AES-encryption)** &nbsp;·&nbsp; <samp>c++</samp><br>
AES-128 built from the S-box up - SubBytes, ShiftRows, MixColumns, key expansion -<br>
chained into a full encrypt/decrypt pipeline verified against the FIPS-197 known-answer test.

**[Risk Assessment Report](https://github.com/WendySpark/risk-assessment-report)** &nbsp;·&nbsp; <samp>security</samp><br>
Full cybersecurity risk assessment for a fictional company: 20 identified risks<br>
across four assets, each matched with a countermeasure and implementation plan.

<img src="./hd-stats.svg" width="620" alt="stats"/>

<div align="center">

<img src="./streak.svg" width="620" alt="Current and longest streak"/>

<img src="./langs.svg" width="620" alt="Top languages by bytes and by repo"/>

<img src="./year.svg" width="620" alt="The last year, one character per day"/>

</div>

<img src="./hd-about-this-page.svg" width="620" alt="about this page"/>

Every graphic on this page is generated, not embedded from anyone else's server.
[`scripts/generate_stats.py`](scripts/generate_stats.py) pulls straight from the
GitHub GraphQL API and draws `stats.svg`, `streak.svg`, `langs.svg`, `year.svg`,
and these section headings, run daily by
[a scheduled action](.github/workflows/stats.yml) that commits only what changed.

Since nothing loads from a third party, nothing here can rate-limit or go dark.
Headings and stats use the viewer's own monospace font stack rather than an
embedded font, so this page stays a plain, dependency-free SVG pipeline.

`year.svg` lays the last ~365 days out GitHub-calendar-shaped (one character per
day, oldest to newest, left to right) using a quiet-to-loud ramp: `·` `:` `+` `#` `@`.
