# ANALYTICAL & STATISTICAL METHODOLOGY
**TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform**

This document establishes the mathematical definitions, statistical algorithms, and epidemiological formulations employed throughout the TRAFFIC TREND platform.

---

## 1. Key Performance Indicators (KPIs)

### 1.1 Total Incidents & Casualty Aggregations
Given a filtered dataset containing $N$ crash events indexed by $i \in \{1, 2, \dots, N\}$:
$$\text{Total Accidents} = N$$
$$\text{Total Fatalities} = \sum_{i=1}^{N} \text{Fatalities}_i$$
$$\text{Total Injured} = \sum_{i=1}^{N} \text{Injured}_i$$
$$\text{Total Casualties} = \text{Total Fatalities} + \text{Total Injured}$$

### 1.2 Fatality Rate (%)
The fatality rate measures the mortality likelihood per recorded crash event:
$$\text{Fatality Rate (\%)} = \left( \frac{\text{Total Fatalities}}{N} \right) \times 100$$

### 1.3 Casualty Rate per Incident
Average number of victims (killed or injured) per collision:
$$\text{Casualty Rate} = \frac{\text{Total Casualties}}{N}$$

### 1.4 Casualty Severity Index (CSI)
Standardized index adapted from transportation safety agencies (e.g. UK RoSPA and Indian MoRTH) weighting mortal harm over non-fatal bodily harm:
$$\text{CSI}_i = (5 \times \text{Fatalities}_i) + (1 \times \text{Injured}_i)$$

### 1.5 Period-over-Period Growth ($\Delta \%$)
For any metric $M$ comparing the active period with the preceding baseline period $M_{\text{prior}}$:
$$\Delta \% = \left( \frac{M_{\text{current}} - M_{\text{prior}}}{M_{\text{prior}}} \right) \times 100$$

---

## 2. Institutional Data Quality Scorecard

The platform calculates a four-dimensional composite quality index ($0.0 - 100.0$):

$$\text{Overall Score} = (0.30 \times C) + (0.25 \times U) + (0.25 \times V) + (0.20 \times K)$$

Where:
1. **Completeness ($C$):**
   $$C = \left( 1 - \frac{\text{Total Missing Cells}}{\text{Total Rows} \times \text{Total Columns}} \right) \times 100$$
2. **Uniqueness ($U$):**
   $$U = \left( 1 - \frac{\text{Duplicate Rows}}{\text{Total Rows}} \right) \times 100$$
3. **Validity ($V$):**
   Percentage of records passing semantic constraints:
   - Valid date format (`YYYY-MM-DD`)
   - Geographic coordinates within $[-90^\circ, +90^\circ]$ latitude and $[-180^\circ, +180^\circ]$ longitude
   - Non-negative casualty values ($\text{Fatalities} \ge 0$, $\text{Injuries} \ge 0$)
4. **Consistency ($K$):**
   Percentage of records maintaining logical integrity between severity category and casualty numbers (e.g., an incident classified as `Fatal` must record $\ge 1$ fatality).

---

## 3. Risk Intelligence & Anomaly Detection

### 3.1 Composite Regional Risk Priority Index (RPI)
To prioritize resource interventions, regions are scored on a balanced scale ($0.0 - 100.0$):
$$\text{RPI}_r = \left[ 0.40 \times \tilde{F}_r + 0.60 \times \tilde{M}_r \right] \times 100$$
Where:
- $\tilde{F}_r$: Min-Max normalized incident frequency for region $r$
- $\tilde{M}_r$: Min-Max normalized fatality rate for region $r$

**Risk Tiers:**
- **Critical Priority:** $\text{RPI} \ge 75.0$
- **High Priority:** $50.0 \le \text{RPI} < 75.0$
- **Moderate Attention:** $25.0 \le \text{RPI} < 50.0$
- **Low Risk Baseline:** $\text{RPI} < 25.0$

### 3.2 Statistical Volume Anomaly Detection ($Z$-Score)
Identifies anomalous surges in crash frequencies across monthly or weekly buckets:
$$Z_t = \frac{x_t - \mu}{\sigma}$$
Where:
- $x_t$: Observed accident volume in period $t$
- $\mu$: Historical mean volume
- $\sigma$: Historical standard deviation

**Surge Classification:**
- **Elevated Surge:** $2.0 \le Z_t < 3.0$ ($p < 0.05$)
- **Critical Surge:** $Z_t \ge 3.0$ ($p < 0.003$)

---

## 4. Time-Series Trajectory Forecasting

### Parametric Linear Trend with Heteroskedastic Dispersion
When at least 8 continuous historical months are present, the baseline trajectory is modeled via least-squares linear regression:
$$\hat{y}_t = \beta_0 + \beta_1 t$$
Confidence bounds (95%) widen dynamically with future horizon step $k$:
$$\text{Margin}_k = 1.96 \times \text{SE} \times \sqrt{1 + \frac{k}{N}}$$
$$\hat{y}_k \pm \text{Margin}_k$$

### Scientific Limitations & Disclaimers
1. **Stationarity Assumption:** Assumes underlying reporting infrastructure and driving behavior remain stable.
2. **Exogenous Factors:** Cannot account for sudden legislative policy changes, infrastructure overhauls, or pandemic disruptions.
3. **Correlation vs Causation:** Observational road safety data cannot establish causality. All associations are empirical correlations.

