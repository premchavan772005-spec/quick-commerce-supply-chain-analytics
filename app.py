import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Supply Chain Control Tower", layout="wide", page_icon="📦")

st.title("📦 Quick-Commerce Supply Chain Control Tower")
st.markdown("**Inventory Deficit Forecasting + Live Stockout Simulator | Operations Research Engine**")

@st.cache_data
def load_data():
    alerts = pd.read_csv("inventory_deficit_alerts.csv")
    shipping = pd.read_csv("raw_shipping_logs.csv")
    return alerts, shipping

alerts_df, shipping_df = load_data()

tab1, tab2, tab3 = st.tabs([
    "🧮 Live Stockout Simulator",
    "🚨 Inventory Alert Dashboard",
    "🚚 Supplier SLA Tracker"
])

with tab1:
    st.subheader("🧮 Live Stockout & Reorder Calculator")
    st.markdown("Enter your warehouse numbers below — the Operations Research engine calculates reorder points **instantly**")

    st.markdown("---")
    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("#### 📥 Warehouse Input Parameters")

        category = st.text_input(
            "📦 Product Category Name",
            value="Electronics",
            help="Enter the product category you want to simulate"
        )

        current_stock = st.number_input(
            "📊 Current Stock on Hand (units)",
            min_value=0, max_value=100000,
            value=500, step=10,
            help="How many units are currently in your warehouse"
        )

        daily_demand = st.number_input(
            "📈 Average Daily Demand (units/day)",
            min_value=1, max_value=10000,
            value=45, step=1,
            help="How many units are sold per day on average"
        )

        demand_std = st.number_input(
            "📉 Demand Variability (std deviation)",
            min_value=0, max_value=1000,
            value=8, step=1,
            help="How much daily demand fluctuates — higher = more unpredictable"
        )

        lead_time = st.number_input(
            "🚚 Supplier Lead Time (days)",
            min_value=1, max_value=30,
            value=4, step=1,
            help="How many days it takes for supplier to deliver after ordering"
        )

        lead_time_std = st.number_input(
            "⏱️ Lead Time Variability (days)",
            min_value=0, max_value=10,
            value=1, step=1,
            help="How much supplier delivery time varies"
        )

        service_level = st.select_slider(
            "🎯 Target Service Level",
            options=["90%", "92%", "95%", "97%", "99%"],
            value="95%",
            help="Higher service level = more safety stock = fewer stockouts"
        )

        seasonal_spike = st.slider(
            "🎉 Seasonal Demand Spike (%)",
            min_value=0, max_value=100,
            value=8, step=5,
            help="Expected % increase during festival/sale season"
        )

        st.markdown("---")
        calculate = st.button("⚡ Calculate Reorder Strategy", use_container_width=True)

    with col_output:
        st.markdown("#### 📤 Operations Research Output")

        z_map = {"90%": 1.282, "92%": 1.405, "95%": 1.645, "97%": 1.881, "99%": 2.326}
        Z = z_map[service_level]

        safety_stock = Z * np.sqrt(
            (lead_time * demand_std**2) + (daily_demand**2 * lead_time_std**2)
        )

        reorder_point = (daily_demand * lead_time) + safety_stock

        days_until_reorder = max(0, (current_stock - reorder_point) / daily_demand)
        days_until_stockout = current_stock / daily_demand

        reorder_date = datetime.today() + timedelta(days=days_until_reorder)
        stockout_date = datetime.today() + timedelta(days=days_until_stockout)

        units_to_order = max(0, reorder_point - current_stock + (daily_demand * lead_time * (1 + seasonal_spike/100)))

        seasonal_demand_14d = daily_demand * 14 * (1 + seasonal_spike/100)

        if current_stock <= reorder_point * 0.5:
            status = "🔴 CRITICAL — ORDER NOW"
            status_color = "#D85A30"
        elif current_stock <= reorder_point:
            status = "🟠 REORDER TRIGGERED"
            status_color = "#E8950A"
        elif days_until_stockout <= 7:
            status = "🟡 MONITOR CLOSELY"
            status_color = "#D4A017"
        else:
            status = "🟢 OPTIMAL STOCK LEVEL"
            status_color = "#1D9E75"

        st.markdown(f"""
        <div style="background:{status_color}22;border-left:5px solid {status_color};
        padding:16px;border-radius:8px;margin-bottom:16px">
        <h3 style="color:{status_color};margin:0">{status}</h3>
        <p style="margin:4px 0 0 0;color:#555;font-size:13px">Category: {category}</p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        m1.metric("🛡️ Safety Stock", f"{safety_stock:,.0f} units")
        m2.metric("📍 Reorder Point", f"{reorder_point:,.0f} units")

        m3, m4 = st.columns(2)
        m3.metric("📅 Days Until Reorder", f"{days_until_reorder:.0f} days",
                  f"Order by {reorder_date.strftime('%d %b')}")
        m4.metric("⚠️ Days Until Stockout", f"{days_until_stockout:.0f} days",
                  f"Stockout on {stockout_date.strftime('%d %b')}" if days_until_stockout < 30 else "Safe for 30+ days",
                  delta_color="inverse")

        m5, m6 = st.columns(2)
        m5.metric("📦 Units to Order Now", f"{units_to_order:,.0f} units")
        m6.metric("📈 14-Day Forecast Demand", f"{seasonal_demand_14d:,.0f} units")

        st.markdown("---")
        st.markdown("#### 📊 Stock Depletion Forecast")

        days_range = list(range(0, 31))
        stock_levels = [max(0, current_stock - (daily_demand * d)) for d in days_range]
        reorder_line = [reorder_point] * 31
        safety_line = [safety_stock] * 31

        fig_sim, ax_sim = plt.subplots(figsize=(7, 3.5))
        ax_sim.plot(days_range, stock_levels, color='#185FA5', linewidth=2.5,
                    label='Projected Stock', marker='o', markersize=3, markevery=5)
        ax_sim.axhline(y=reorder_point, color='#E8950A', linewidth=1.5,
                       linestyle='--', label=f'Reorder Point ({reorder_point:,.0f})')
        ax_sim.axhline(y=safety_stock, color='#D85A30', linewidth=1.5,
                       linestyle=':', label=f'Safety Stock ({safety_stock:,.0f})')
        ax_sim.fill_between(days_range, stock_levels, safety_stock,
                            where=[s > safety_stock for s in stock_levels],
                            alpha=0.1, color='#185FA5')
        ax_sim.set_xlabel("Days from Today")
        ax_sim.set_ylabel("Stock Units")
        ax_sim.set_title(f"30-Day Stock Depletion Curve — {category}", fontweight='bold')
        ax_sim.legend(fontsize=8)
        ax_sim.grid(alpha=0.3)
        ax_sim.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        st.pyplot(fig_sim)

        st.markdown(f"""
        <div style="background:#E6F1FB;border-radius:8px;padding:12px;font-size:12px;color:#333">
        <b>📋 Reorder Recommendation:</b> Place an order for <b>{units_to_order:,.0f} units</b> of <b>{category}</b>
        by <b>{reorder_date.strftime('%d %b %Y')}</b> to maintain {service_level} service level
        through the upcoming {seasonal_spike}% seasonal demand spike.
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("🚨 Live Inventory Deficit Alert Dashboard")

    total_deficit = alerts_df['stock_deficit_qty'].sum() if 'stock_deficit_qty' in alerts_df.columns else 0
    critical_count = len(alerts_df[alerts_df['operational_status'] == 'CRITICAL STOCKOUT RISK']) if 'operational_status' in alerts_df.columns else 0
    reorder_count = len(alerts_df[alerts_df['operational_status'] == 'REORDER TRIGGERED']) if 'operational_status' in alerts_df.columns else 0
    total_categories = len(alerts_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Categories at Risk", f"{total_categories}")
    c2.metric("🔴 Critical Stockout", f"{critical_count}")
    c3.metric("🟠 Reorder Triggered", f"{reorder_count}")
    c4.metric("📉 Total Units Deficit", f"{total_deficit:,.0f}")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📋 Deficit Alert Grid")
        if 'operational_status' in alerts_df.columns:
            def color_status(val):
                if val == 'CRITICAL STOCKOUT RISK':
                    return 'background-color: #FAECE7; color: #D85A30; font-weight: bold'
                elif val == 'REORDER TRIGGERED':
                    return 'background-color: #FEF3E2; color: #E8950A; font-weight: bold'
                return ''

            display_df = alerts_df.copy()
            if 'stock_deficit_qty' in display_df.columns:
                display_df = display_df.sort_values('stock_deficit_qty', ascending=False)

            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )

    with col_b:
        st.subheader("📊 Deficit by Category")
        if 'stock_deficit_qty' in alerts_df.columns and 'category_name' in alerts_df.columns:
            top_deficit = alerts_df.nlargest(10, 'stock_deficit_qty')
            fig_def, ax_def = plt.subplots(figsize=(7, 5))
            colors_def = ['#D85A30' if s == 'CRITICAL STOCKOUT RISK' else '#E8950A'
                          for s in top_deficit.get('operational_status', ['REORDER TRIGGERED']*len(top_deficit))]
            bars_def = ax_def.barh(top_deficit['category_name'],
                                   top_deficit['stock_deficit_qty'],
                                   color=colors_def, edgecolor='white')
            ax_def.set_xlabel("Units Deficit")
            ax_def.set_title("Top 10 Categories by Stock Deficit", fontweight='bold')
            for bar, val in zip(bars_def, top_deficit['stock_deficit_qty']):
                ax_def.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                            f'{val:,.1f}', va='center', fontsize=8)
            ax_def.grid(axis='x', alpha=0.3)
            red_patch = mpatches.Patch(color='#D85A30', label='Critical Stockout')
            orange_patch = mpatches.Patch(color='#E8950A', label='Reorder Triggered')
            ax_def.legend(handles=[red_patch, orange_patch], fontsize=8)
            st.pyplot(fig_def)

    if 'reorder_point_threshold' in alerts_df.columns and 'current_warehouse_est_stock' in alerts_df.columns:
        st.subheader("📈 Stock vs Reorder Point Comparison")
        fig_comp, ax_comp = plt.subplots(figsize=(12, 4))
        x = np.arange(len(alerts_df['category_name']))
        width = 0.35
        ax_comp.bar(x - width/2, alerts_df['current_warehouse_est_stock'],
                    width, label='Current Stock', color='#185FA5', alpha=0.8, edgecolor='white')
        ax_comp.bar(x + width/2, alerts_df['reorder_point_threshold'],
                    width, label='Reorder Point (ROP)', color='#D85A30', alpha=0.8, edgecolor='white')
        ax_comp.set_xlabel("Product Category")
        ax_comp.set_ylabel("Units")
        ax_comp.set_title("Current Stock vs Reorder Point Threshold — All At-Risk Categories", fontweight='bold')
        ax_comp.set_xticks(x)
        ax_comp.set_xticklabels(alerts_df['category_name'], rotation=45, ha='right', fontsize=7)
        ax_comp.legend()
        ax_comp.grid(axis='y', alpha=0.3)
        st.pyplot(fig_comp)

with tab3:
    st.subheader("🚚 Supplier SLA Performance Tracker")
    st.markdown("Comparing actual vs promised delivery times across all shipping modes")

    if 'days_for_shipping_real' in shipping_df.columns and 'shipping_mode' in shipping_df.columns:

        sla_summary = shipping_df.groupby('shipping_mode').agg(
            Avg_Actual_Days=('days_for_shipping_real', 'mean'),
            Avg_Scheduled_Days=('days_for_shipment_scheduled', 'mean'),
            Total_Orders=('shipping_mode', 'count')
        ).reset_index()

        sla_summary['SLA_Breach_%'] = ((sla_summary['Avg_Actual_Days'] -
                                        sla_summary['Avg_Scheduled_Days']) /
                                       sla_summary['Avg_Scheduled_Days'] * 100).round(1)

        sla_summary['Status'] = sla_summary['SLA_Breach_%'].apply(
            lambda x: '🔴 Breaching SLA' if x > 10 else ('🟠 Near Breach' if x > 0 else '🟢 On Time')
        )

        s1, s2, s3 = st.columns(3)
        s1.metric("Shipping Modes Tracked", len(sla_summary))
        s2.metric("Avg Actual Lead Time",
                  f"{shipping_df['days_for_shipping_real'].mean():.1f} days")
        s3.metric("Avg Scheduled Lead Time",
                  f"{shipping_df['days_for_shipment_scheduled'].mean():.1f} days")

        st.divider()
        col_c, col_d = st.columns(2)

        with col_c:
            st.subheader("📊 Actual vs Scheduled Delivery")
            fig_sla, ax_sla = plt.subplots(figsize=(7, 4))
            x_sla = np.arange(len(sla_summary))
            w = 0.35
            ax_sla.bar(x_sla - w/2, sla_summary['Avg_Actual_Days'],
                       w, label='Actual Days', color='#D85A30', edgecolor='white')
            ax_sla.bar(x_sla + w/2, sla_summary['Avg_Scheduled_Days'],
                       w, label='Scheduled Days', color='#1D9E75', edgecolor='white')
            ax_sla.set_xticks(x_sla)
            ax_sla.set_xticklabels(sla_summary['shipping_mode'], rotation=20, ha='right', fontsize=9)
            ax_sla.set_ylabel("Average Days")
            ax_sla.set_title("Supplier SLA: Actual vs Promised Delivery", fontweight='bold')
            ax_sla.legend()
            ax_sla.grid(axis='y', alpha=0.3)
            for i, (act, sch) in enumerate(zip(sla_summary['Avg_Actual_Days'],
                                               sla_summary['Avg_Scheduled_Days'])):
                ax_sla.text(i - w/2, act + 0.05, f'{act:.1f}', ha='center', fontsize=8)
                ax_sla.text(i + w/2, sch + 0.05, f'{sch:.1f}', ha='center', fontsize=8)
            st.pyplot(fig_sla)

        with col_d:
            st.subheader("📋 SLA Breach Summary")
            st.dataframe(
                sla_summary[['shipping_mode', 'Avg_Actual_Days',
                              'Avg_Scheduled_Days', 'SLA_Breach_%',
                              'Total_Orders', 'Status']],
                use_container_width=True,
                height=300
            )

            st.subheader("📦 Order Volume by Shipping Mode")
            fig_vol, ax_vol = plt.subplots(figsize=(7, 3))
            ax_vol.bar(sla_summary['shipping_mode'], sla_summary['Total_Orders'],
                       color='#185FA5', edgecolor='white')
            ax_vol.set_ylabel("Number of Orders")
            ax_vol.set_title("Order Volume by Shipping Mode", fontweight='bold')
            plt.xticks(rotation=20, ha='right', fontsize=9)
            ax_vol.grid(axis='y', alpha=0.3)
            st.pyplot(fig_vol)

        st.subheader("🔍 Shipping Delay Distribution")
        shipping_df['Delay_Days'] = (shipping_df['days_for_shipping_real'] -
                                     shipping_df['days_for_shipment_scheduled'])
        fig_delay, ax_delay = plt.subplots(figsize=(12, 3.5))
        for mode, color in zip(shipping_df['shipping_mode'].unique(),
                                ['#185FA5', '#1D9E75', '#D85A30', '#E8950A']):
            mode_data = shipping_df[shipping_df['shipping_mode'] == mode]['Delay_Days']
            ax_delay.hist(mode_data, bins=20, alpha=0.6, label=mode,
                          color=color, edgecolor='white')
        ax_delay.axvline(x=0, color='black', linewidth=1.5, linestyle='--', label='On-Time Line')
        ax_delay.set_xlabel("Delay (days) — Negative = Early, Positive = Late")
        ax_delay.set_ylabel("Number of Orders")
        ax_delay.set_title("Shipping Delay Distribution by Mode", fontweight='bold')
        ax_delay.legend(fontsize=8)
        ax_delay.grid(alpha=0.3)
        st.pyplot(fig_delay)

st.divider()
st.caption("📦 Built by Prem Chavan | Quick-Commerce Supply Chain Control Tower | github.com/premchavan772005-spec")
