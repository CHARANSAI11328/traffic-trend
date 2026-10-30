# ANALYTICAL METHODOLOGY & STATISTICAL FORMULATION
## TRAFFIC TREND — Road Safety Intelligence & Accident Analytics Platform
*Document Version: 2.0.0 | Academic & Production Standard*

---

## 1. Executive Summary & Purpose

The **TRAFFIC TREND** platform employs rigorous, mathematically grounded data science formulations to extract actionable road safety intelligence from accident records. This document establishes the formal definitions, statistical methodologies, equations, and analytical caveats governing every metric, chart, and scorecard produced by the platform.

---

## 2. Executive Key Performance Indicators (KPIs)

All executive indicators are dynamically evaluated from verified database queries over filtered DataFrame slices:

### 2.1 Primary Volume and Casualty Metrics

- **Total Recorded Accidents ($N$):**
  $$N = \sum_{i=1}^{m} 1$$
  Represents the count of unique crash events within the selected horizon.

- **Total Fatalities ($F$):**
  $$F = \sum_{i=1}^{m} \text{fatalities\_count}_i$$
  Represents human lives lost across all crash occurrences.

- **Total Injured Persons ($I$):**
  $$I = \sum_{i=1}^{m} \text{injured\_count}_i$$
  Represents grievous and minor injuries sustained.

- **Total Casualties ($C$):**
  $$C = F + I$$
  *Methodology Rule:* Casualty count must never be conflated with crash event count. A single collision involving a bus may produce multiple casualties ($C \ge 1, N = 1$).

- **Fatal Accident Ratio ($FAR$):**
  $$FAR = \left( \frac{\sum_{i=1}^{m} \mathbb{I}(\text{is\_fatal}_i)}{N} \right) \times 100$$
  where $\mathbb{I}(\text{is\_fatal}_i) = 1$ if $\text{fatalities}_i > 0$ or $\text{severity}_i = \text{'Fatal'}$, else $0$.

- **Fatality Rate per 100 Accidents ($FR$):**
  $$FR = \left( \frac{F}{N} \right) \times 100$$
  Measures lethal casualty density per 100 incident occurrences.

- **Casualty Rate per Crash ($CR$):**
  $$CR = \frac{C}{N}$$

- **Average Accidents per Day ($APD$):**
  $$APD = \frac{N}{\max(1, \Delta \text{days})}$$
  where $\Delta \text{days} = \text{Date}_{\max} - \text{Date}_{\min} + 1$.

- **Period-over-Period Delta ($\Delta\%$):**
  $$\Delta\% = \left( \frac{M_{\text{current}} - M_{\text{prior}}}{M_{\text{prior}}} \right) \times 100$$
  Evaluated against preceding equivalent periods (prior calendar year or prior temporal horizon). Negative deltas in fatalities or accidents indicate favorable reduction.

---

## 3. Geographical Intelligence & Hotspot Ranking

### 3.1 Composite Regional Risk Score ($RSI$)

To prioritize administrative jurisdictions and corridors requiring urgent engineering intervention without distorting low-volume outliers, a weighted composite index is computed:

$$RSI_j = (N_j \times 0.4) + (F_j \times 2.5) + (I_j \times 0.8)$$

- **Weight Rationale:**
  - $2.5$ for fatalities reflects the paramount human cost and societal loss.
  - $0.8$ for injuries incorporates severe and minor bodily harm.
  - $0.4$ for incident volume captures infrastructural collision frequency.

### 3.2 High-Risk Spatial Corridor Identification

Corridors are defined as $(District \times RoadType)$ intersections. A corridor is designated as a **Critical Blackspot** when:
$$\text{Fatalities}_k \ge 10 \quad \text{and} \quad N_k \ge 15$$

---

## 4. Temporal Intelligence & Diurnal Analysis

### 4.1 Year-over-Year Growth (YoY%)
$$\text{YoY\%}_t = \left( \frac{N_t - N_{t-1}}{N_{t-1}} \right) \times 100$$

### 4.2 Peak Diurnal Rush Hour Threshold
An hour $h \in [0, 23]$ is flagged as a **Peak Crash Window** if:
$$N_h \ge Q_{0.75}(\{N_0, N_1, \dots, N_{23}\})$$
representing hours exceeding the 75th percentile of diurnal crash frequency.

### 4.3 2D Day-Hour Collision Density Heatmap
Visualizes the bivariate frequency distribution:
$$M(d, h) = \sum_{i=1}^{m} \mathbb{I}(\text{day}_i = d \land \text{hour}_i = h)$$
where $d \in [0, 6]$ (Monday–Sunday) and $h \in [0, 23]$.

---

## 5. Risk Intelligence & Statistical Anomaly Detection

To identify genuinely anomalous spikes rather than random Poisson noise, two complementary tests are executed:

### 5.1 Parametric $Z$-Score Test
$$Z_j = \frac{X_j - \mu_X}{\sigma_X}$$
- $X_j$: Observed crash volume or fatality rate in region $j$.
- $\mu_X, \sigma_X$: Empirical mean and sample standard deviation across comparable entities.
- **Threshold:** $|Z_j| > 1.96$ corresponds to a two-tailed $\alpha = 0.05$ significance level.

### 5.2 Tukey Interquartile Range (IQR) Outlier Detection
For non-Gaussian, skewed regional crash distributions:
$$IQR = Q_3 - Q_1$$
$$\text{Upper Fence} = Q_3 + (1.5 \times IQR)$$
Entities with $X_j > \text{Upper Fence}$ are designated as statistical outliers.

---

## 6. Econometric Time-Series Forecasting

### 6.1 Ordinary Least Squares (OLS) Trend Fitting
Monthly historical accident volume $y_t$ is modeled as:
$$\hat{y}_t = \beta_0 + \beta_1 t$$
where:
$$\beta_1 = \frac{\sum (t - \bar{t})(y_t - \bar{y})}{\sum (t - \bar{t})^2}, \quad \beta_0 = \bar{y} - \beta_1 \bar{t}$$

### 6.2 Empirical Confidence Intervals
For future horizon periods $t + k$:
$$\hat{y}_{t+k} \pm 1.96 \cdot s_{\epsilon} \sqrt{1 + 0.15 \cdot k}$$
where $s_{\epsilon} = \sqrt{\frac{1}{n-2} \sum (y_t - \hat{y}_t)^2}$ is the standard error of regression residuals. The $\sqrt{1 + 0.15 \cdot k}$ multiplier accounts for increasing forecasting uncertainty over expanding horizons.

---

## 7. Data Quality Scorecard Formulation

The institutional scorecard evaluates datasets across 4 weighted mathematical dimensions (0–100 scale):

$$\text{Overall Score} = (0.30 \times C) + (0.25 \times U) + (0.25 \times V) + (0.20 \times K)$$

1. **Completeness ($C$, 30%):**
   $$C = \max\left(0, \left(1 - \frac{\text{Missing Cells}}{\text{Total Cells}}\right) \times 100\right)$$
2. **Uniqueness ($U$, 25%):**
   $$U = \max\left(0, \left(1 - \frac{\text{Duplicate Rows}}{\text{Total Rows}}\right) \times 100\right)$$
3. **Validity ($V$, 25%):**
   Conformity of date strings (ISO 8601), geographical latitude $[-90, 90]$, and longitude $[-180, 180]$.
4. **Consistency ($K$, 20%):**
   Logical agreement between casualty counts and severity labels (e.g., verifying that collisions marked 'Fatal' do not have 0 recorded fatalities).

- **Grading Scale:**
  - $\ge 90$: Institutional Grade (A)
  - $75 - 89$: Good / Minor Remediation Recommended (B)
  - $60 - 74$: Fair / Cleaning Required (C)
  - $< 60$: Poor / High Risk of Analytical Distortion (D)

---

## 8. Analytical Caveats & Scientific Integrity

1. **Correlation vs Causation:**
   Statistical correlations between weather/road types and crash counts describe historical patterns. They do not constitute deterministic proof of sole causation without controlled counterfactuals.
2. **Exposure & Denominator Bias:**
   High raw crash volume in a populous state or high-traffic highway does not imply higher inherent danger per traveler without vehicle-miles traveled (VMT) or population normalization.
3. **Live Telemetry Distinction:**
   Published police and government transport records are periodic historical datasets. The platform explicitly labels live feed status as disconnected unless authorized telemetry streams are configured.
