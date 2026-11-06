# ⚡ Electric Bus Fleet Charging & Timetable Optimizer

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PuLP](https://img.shields.io/badge/PuLP-Optimization-2E7D32?style=flat-square&logoColor=white)](https://coin-or.github.io/pulp/)
[![BME Budapest](https://img.shields.io/badge/BME-Transportation_Engineering-800000?style=flat-square)](https://www.bme.hu/?language=en)
[![BKK Budapest](https://img.shields.io/badge/Case_Study-Budapest_BKK-5B2C6F?style=flat-square)](https://bkk.hu/en/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

> **M.Sc. Research Project — Faculty of Transportation Engineering & Vehicle Engineering**  
> **Department of Transport Technology and Economics, Budapest University of Technology and Economics (BME)**  
> **Authors:** Recep Eren Durgut, Joywin Jebii Tomno, Daisy Machanja, Mateo Andrade  
> **Case Study:** Electrification of solo municipal bus lines operating through Budapest's **Újpest-Központ** terminal (Lines **25, 147, 170, 220, 270**).

---

## 📌 Project Background & Motivation

Decarbonizing urban public transit requires transitioning conventional Internal Combustion Engine (ICE) buses to Battery Electric Buses (BEBs). However, fleet operators face significant operational and infrastructure challenges:
1. **Limited battery capacity & driving range.**
2. **Dynamic time-of-use (ToU) electricity tariffs and grid capacity constraints.**
3. **Deadhead kilometers** to central charging depots versus opportunity charging at terminals.
4. **Timetable synchronization:** Charging events must align seamlessly with existing headway schedules without disrupting service reliability.

This project formulates and solves a **Linear Programming (LP / MILP)** model with **PuLP** to optimize fleet scheduling, battery State-of-Charge (SoC), and charging assignments at Budapest's **Újpest-Központ** transportation hub.

---

## 🔬 Mathematical Formulation & Optimization Logic

The model minimizes total operational expenditures while strictly respecting physical, temporal, and grid constraints:

$$\min \quad \sum_{t \in T} \sum_{b \in B} \left( c_t^{\text{grid}} \cdot P_{b,t}^{\text{charge}} + c^{\text{idle}} \cdot I_{b,t} + c^{\text{deadhead}} \cdot D_{b,t} \right)$$

### Key Operational Constraints:
* **Energy Balance & SoC Dynamics:**
  $$\text{SoC}_{b, t+1} = \text{SoC}_{b, t} + \eta \cdot P_{b,t}^{\text{charge}} \cdot \Delta t - E_{b,t}^{\text{trip}} \quad \forall b \in B, t \in T$$
* **Battery Protection Thresholds:**
  $$\text{SoC}^{\min} \le \text{SoC}_{b,t} \le \text{SoC}^{\max} \quad \forall b \in B, t \in T$$
* **Terminal Charger Power & Bay Limits:**
  $$\sum_{b \in B} P_{b,t}^{\text{charge}} \le P_t^{\text{station\_limit}} \quad \forall t \in T$$
* **Timetable Coverage:** All scheduled trips across BKK Lines 25, 147, 170, 220, and 270 must be serviced on time.

---

## 📂 Repository Structure

```text
├── bus_schedule_optimizer.py      # Core PuLP Linear Programming optimization engine
├── fleet_simulation.py            # Object-oriented bus, driver & battery simulation model
├── LP_Optimization_Analysis.ipynb # Jupyter notebook for parametric sensitivity & plots
├── requirements.txt               # Dependencies (pulp, pandas, numpy)
├── data/
│   ├── schedule.csv               # BKK departure and headway logs (Újpest-Központ)
│   ├── charging_capacity.csv      # Time-dependent station capacity & power limits
│   ├── cost_matrix.csv            # Line-to-depot deadhead and operational cost matrix
│   └── node_costs.csv             # Route node costs
└── docs/
    ├── Electromobility_Presentation_Final.pdf  # Final defense presentation deck
    └── Electromobility_Report_Final.docx       # Full technical research report
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* Recommended: Virtual environment

### Installation

```bash
# 1. Clone repository
git clone https://github.com/rerendurgut/ev-fleet-charging-optimizer.git
cd ev-fleet-charging-optimizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run schedule optimizer
python bus_schedule_optimizer.py
```

---

## 📑 Research Documents

Detailed background, route maps, energy consumption benchmarks (kWh/km), and cost-benefit trade-offs are available in the [`docs/`](docs/) directory:
* [Electromobility Final Presentation (PDF)](docs/Electromobility_Presentation_Final.pdf)
* [Electromobility Final Report](docs/Electromobility_Report_Final.docx)

---

## 📜 License

MIT License. Developed for research at Budapest University of Technology and Economics (BME).
