# DemBench v2.0.0 — Modern UI & 3D GPU Benchmark

## Yenilikler

### UI Modernizasyonu
- **Neon Dark Theme** — Derin koyu lacivert arka plan ile modern neon renk paleti
- **Renk kodlu benchmark kartları** — CPU: Mavi, RAM: Mor, Disk: Turuncu, GPU: Pembe, Network: Teal
- **Glassmorphism efektleri** — Accent stripe, elevated surface, border katmanları
- **JetBrains Mono** monospace font skorlar için
- **Gelişmiş summary kartı** — Altın çerçeveli skor kutusu, tier badge sistemi

### GPU Testi 3D Modernizasyon
- 2D üçgenler yerine **tam 3D animasyonlu sahne**
- Dönen küp, 6 yörünge küre, torus halka, 4 piramit, 12 küçük dönen küp, zemin ızgarası
- **OpenGL**: Lighting (2 ışık kaynağı), depth testing, perspective projection, smooth shading
- **Dinamik kamera** orbiti
- **512x512 viewport** (önceki 128x128)

### Bug Düzeltmeleri
- GPU JSON parsing hatası düzeltildi
- CPU multi-core negatif skor sorunu giderildi
- Thread-safe UI güncellemeleri iyileştirildi
- Hata loglama encoding koruması eklendi

---

## Kurulum (Kaynak Koddan)

```bash
pip install -r requirements.txt
python main.py
```

## Platform Build

| Platform | Komut | Çıktı |
|----------|-------|-------|
| **Windows** | `build_windows.bat` | `dist\DemBench.exe` |
| **Linux** | `bash build_linux.sh` | `dist/DemBench` |
| **macOS** | `bash build_macos.sh` | `dist/DemBench.app` / `.dmg` |

> Build için **Python 3.10+** ve **PyInstaller** gereklidir.

## Sistem Gereksinimleri
- Python 3.10+
- OpenGL destekli GPU (GPU testi için)
- 2 GB RAM (minimum)
- Windows 10+ / Linux (X11/Wayland) / macOS 11+
