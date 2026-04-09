import json
import plotly.graph_objects as go
from analysis import connect_db, extract_data, compute_kpis


def load_config():
    """Load KPI thresholds from config.json"""
    with open("config.json", "r") as f:
        return json.load(f)


def evaluate_kpi(value, threshold):
    """Return color status based on value vs threshold"""
    if value >= threshold:
        return "GREEN"
    elif value >= threshold * 0.7:
        return "YELLOW"
    else:
        return "RED"


def main():
    
    config = load_config()

    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)

    
    results = {}

    monthly_value = kpis['monthly_revenue'].iloc[-1]
    results['monthly_revenue'] = (
        monthly_value,
        evaluate_kpi(monthly_value, config['monthly_revenue'])
    )

    weekly_value = kpis['weekly_orders'].iloc[-1]
    results['weekly_orders'] = (
        weekly_value,
        evaluate_kpi(weekly_value, config['weekly_orders'])
    )

    
    aov_value = kpis['aov_category'].mean()
    results['aov_category'] = (
        aov_value,
        evaluate_kpi(aov_value, config['aov_category'])
    )

    
    retention_value = kpis['retention_rate']
    results['customer_retention'] = (
        retention_value,
        evaluate_kpi(retention_value, config['customer_retention'])
    )

   
    top_value = kpis['top_products'].iloc[0]  
    results['top_products'] = (
        top_value,
        evaluate_kpi(top_value, config['top_products'])
    )

    
    print("\n=== KPI STATUS ===")
    for k, (val, status) in results.items():
        print(f"{k}: {val:.2f} → {status}")

    
    kpi_names = list(results.keys())
    values = [results[k][0] for k in kpi_names]
    targets = [config[k] for k in kpi_names]

    fig = go.Figure()

    for i, name in enumerate(kpi_names):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=values[i],
            title={'text': name},
            gauge={
                'axis': {'range': [0, targets[i] * 1.5]},
                'steps': [
                    {'range': [0, targets[i] * 0.7], 'color': "red"},
                    {'range': [targets[i] * 0.7, targets[i]], 'color': "yellow"},
                    {'range': [targets[i], targets[i] * 1.5], 'color': "green"}
                ]
            },
            domain={'x': [0, 1], 'y': [0, 1]} 
        ))

    
    buttons = []
    for i, name in enumerate(kpi_names):
        visibility = [False] * len(kpi_names)
        visibility[i] = True
        buttons.append(dict(
            label=name,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"KPI: {name}"}]
        ))

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True
        )],
        title="Interactive KPI Monitor"
    )

    
    fig.write_html("output/kpi_monitor.html")
    print("Interactive KPI monitor saved to output/kpi_monitor.html")


if __name__ == "__main__":
    main()