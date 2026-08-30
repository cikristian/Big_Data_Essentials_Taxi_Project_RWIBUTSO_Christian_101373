#!/usr/bin/env python
"""
Generate all 7 required visualizations (Section 14) from the merged
Hadoop Streaming reducer output files.

Expects these files to exist in DATA_DIR (created via `hdfs dfs -getmerge`):
    results_hourly.tsv     hour \t count
    results_daily.tsv      day_name \t count
    results_locations.tsv  zone \t count
    results_revenue.tsv    zone \t count \t sum_fare \t sum_tip \t sum_total \t avg_fare \t avg_distance
    results_payment.tsv    label \t count \t sum_total \t avg_fare \t avg_tip
    results_distance.tsv   category \t count \t avg_distance \t avg_fare \t avg_total \t fare_per_mile
    results_routes.tsv     route \t count \t sum_total

Outputs 7 PNG files into OUTPUT_DIR.

Usage:
    python make_visualizations.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = r"C:\Users\Christian\OneDrive\Desktop\AUCA_Masters\BigData_Essentials\big-data-essentials-assignment-main\Data"
OUTPUT_DIR = os.path.join(DATA_DIR, "charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["figure.dpi"] = 120


def savefig(name):
    path = os.path.join(OUTPUT_DIR, name)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ---------------------------------------------------------------------
# 1. Trips by hour
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_hourly.tsv"), sep="\t",
                  header=None, names=["hour", "count"])
df["hour"] = df["hour"].astype(int)
df = df.sort_values("hour")

plt.bar(df["hour"], df["count"], color="#3B82F6")
plt.title("Taxi Trips by Hour of Day")
plt.xlabel("Hour (0-23)")
plt.ylabel("Number of Trips")
plt.xticks(range(0, 24))
savefig("01_trips_by_hour.png")


# ---------------------------------------------------------------------
# 2. Trips by day of week
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_daily.tsv"), sep="\t",
                  header=None, names=["day", "count"])
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["day"] = pd.Categorical(df["day"], categories=day_order, ordered=True)
df = df.sort_values("day")

colors = ["#3B82F6"] * 5 + ["#F59E0B"] * 2  # weekdays blue, weekend orange
plt.bar(df["day"], df["count"], color=colors)
plt.title("Taxi Trips by Day of Week (Weekday vs Weekend)")
plt.xlabel("Day of Week")
plt.ylabel("Number of Trips")
plt.xticks(rotation=30)
savefig("02_trips_by_day_of_week.png")


# ---------------------------------------------------------------------
# 3. Top 10 pickup zones
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_locations.tsv"), sep="\t",
                  header=None, names=["zone", "count"])
top10 = df.sort_values("count", ascending=False).head(10).sort_values("count")

plt.barh(top10["zone"], top10["count"], color="#10B981")
plt.title("Top 10 Pickup Zones by Trip Count")
plt.xlabel("Number of Trips")
plt.ylabel("Pickup Zone")
savefig("03_top10_pickup_zones.png")


# ---------------------------------------------------------------------
# 4. Revenue by payment method
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_payment.tsv"), sep="\t",
                  header=None, names=["method", "count", "total_revenue", "avg_fare", "avg_tip"])
df = df.sort_values("total_revenue", ascending=False)

plt.bar(df["method"], df["total_revenue"], color="#8B5CF6")
plt.title("Total Revenue by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Total Revenue ($)")
savefig("04_revenue_by_payment_method.png")


# ---------------------------------------------------------------------
# 5. Trips by distance category
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_distance.tsv"), sep="\t",
                  header=None,
                  names=["category", "count", "avg_distance", "avg_fare", "avg_total", "fare_per_mile"])
cat_order = ["0-2 miles", "2-5 miles", "5-10 miles", "10-20 miles", "20+ miles"]
df["category"] = pd.Categorical(df["category"], categories=cat_order, ordered=True)
df = df.sort_values("category")

plt.bar(df["category"], df["count"], color="#EF4444")
plt.title("Taxi Trips by Distance Category")
plt.xlabel("Distance Category")
plt.ylabel("Number of Trips")
savefig("05_trips_by_distance_category.png")


# ---------------------------------------------------------------------
# 6. Top 10 routes (by trip count)
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_routes.tsv"), sep="\t",
                  header=None, names=["route", "count", "total_revenue"])
top10 = df.sort_values("count", ascending=False).head(10).sort_values("count")

plt.barh(top10["route"], top10["count"], color="#06B6D4")
plt.title("Top 10 Pickup-Dropoff Routes by Trip Count")
plt.xlabel("Number of Trips")
plt.ylabel("Route")
savefig("06_top10_routes.png")


# ---------------------------------------------------------------------
# 7. Revenue vs distance (avg revenue per distance category)
# ---------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "results_distance.tsv"), sep="\t",
                  header=None,
                  names=["category", "count", "avg_distance", "avg_fare", "avg_total", "fare_per_mile"])
cat_order = ["0-2 miles", "2-5 miles", "5-10 miles", "10-20 miles", "20+ miles"]
df["category"] = pd.Categorical(df["category"], categories=cat_order, ordered=True)
df = df.sort_values("category")

fig, ax1 = plt.subplots()
ax1.bar(df["category"].astype(str), df["avg_total"], color="#F97316", label="Avg Revenue ($)")
ax1.set_xlabel("Distance Category")
ax1.set_ylabel("Average Revenue per Trip ($)", color="#F97316")
ax1.set_title("Average Revenue vs Distance Category")

ax2 = ax1.twinx()
ax2.plot(df["category"].astype(str), df["avg_distance"], color="#1D4ED8", marker="o", linewidth=2, label="Avg Distance (mi)")
ax2.set_ylabel("Average Distance (miles)", color="#1D4ED8")

savefig("07_revenue_vs_distance.png")

print("\nAll 7 visualizations generated successfully.")
print(f"Find them in: {OUTPUT_DIR}")
