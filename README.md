# 🔭 KSAS - Kaesar Star Analysis System
### Autonomous Exoplanet Hunter (v4.0 Professional Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-stable-green)

**KSAS** is a professional-grade, autonomous software designed to detect exoplanet candidates from TESS (Transiting Exoplanet Survey Satellite) light curves. It combines fast **Box Least Squares (BLS)** detection with accurate **Transit Least Squares (TLS)** confirmation and strict astrophysical vetting to minimize false positives.

---

## ✨ Key Features

*   **🚀 High-Performance Pipeline:** Multi-threaded architecture processes hundreds of stars per hour.
*   **🔬 Dual Analysis Engine:**
    *   **BLS:** Rapid initial detection of periodic signals.
    *   **TLS:** Physically accurate transit modeling for confirmation.
*   **🛡️ Strict Vetting System:**
    *   **Odd/Even Test:** Rejects eclipsing binaries.
    *   **Shape Test:** Distinguishes planetary U-shapes from binary V-shapes.
    *   **Secondary Eclipse Check:** Filters out self-luminous companions.
*   **🖥️ Professional GUI:**
    *   Real-time light curve visualization.
    *   **Candidate Manager** to track and classify discoveries.
    *   **Quality Scanner** to rank candidates by scientific merit.
    *   **TIC Verifier** for checking external databases (ExoFOP, NASA).
*   **⚙️ Fully Configurable:** Centralized `config.py` for tuning thresholds and sensitivity.

---

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Cesargg55/KSAS.git
    cd KSAS
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Requires: `lightkurve`, `numpy`, `scipy`, `matplotlib`, `transitleastsquares`, `astropy`, `requests`)*

---

## 🚀 Usage

### 1. Start the Hunter
Run the main batch file to start the autonomous hunter:
```bash
ejecutar_ksas.bat
```
*The system will automatically download TESS data, analyze it, and save promising candidates to `candidates.json`.*

### 2. Review Candidates
Open the **Candidate Manager** or **Scanner** from the GUI to review your findings.
*   **Green (EXCELLENT):** High priority. Strong signal, passed all vetting.
*   **Yellow (FAIR):** Caution. Likely false positive or weak signal.

### 3. Re-Scan (Optional)
If you change configuration thresholds, re-analyze existing candidates:
```bash
rescan_candidatos.bat
```

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built for the search for new worlds.* 🌍✨
