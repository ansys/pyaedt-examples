# ✅ Full breakdown

**PVC CAT6A S/STP 4x2 AWG25/7 GY**

Each part encodes a **specific physical and electrical property** of the cable.

# 1) CAT6A → performance class

- **CAT6A (Category 6A)** = “Augmented Cat6”
- Designed for:
  - **10 Gbit/s Ethernet (10GBASE‑T)**
  - Frequencies up to ~500 MHz

👉 Implication for your HFSS model:

- You must capture **high-frequency effects** (skin effect, dielectric loss, coupling)
- Crosstalk (especially **alien crosstalk**) becomes very relevant

# 2) Datasheet

Use the [Belden 10GXE02 datasheet](https://catalog.belden.com/techdata/EN/10GXE02_techdata.pdf) as a reference for building the cable bundle. 