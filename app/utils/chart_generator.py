import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_sales_chart_figure(dates, sales_amounts):
    """
    Returns a Matplotlib Figure for sales trend over time styled for Light Theme with Indian Rupees (₹).
    """
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=100)
    fig.patch.set_facecolor('#ffffff')  # White figure background
    ax.set_facecolor('#f8fafc')         # Slate 50 plot area background
    
    if dates and sales_amounts:
        ax.plot(dates, sales_amounts, marker='o', color='#0284c7', linewidth=2.5, markersize=6, label='Sales (₹)')
        ax.fill_between(dates, sales_amounts, color='#0284c7', alpha=0.15)
    else:
        ax.text(0.5, 0.5, 'No Sales Data Available', color='#64748b', ha='center', va='center', fontsize=12)

    ax.set_title('Recent Sales Performance (₹)', color='#0f172a', fontsize=12, pad=12, fontweight='bold')
    ax.tick_params(colors='#334155', labelsize=8)
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.spines['top'].set_color('#cbd5e1')
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['right'].set_color('#cbd5e1')
    ax.grid(True, linestyle='--', alpha=0.3, color='#cbd5e1')
    plt.xticks(rotation=25)
    plt.tight_layout()
    return fig

def generate_category_stock_figure(categories, stock_counts):
    """
    Returns a Matplotlib bar chart Figure for Stock Quantity by Category styled for Light Theme.
    """
    fig, ax = plt.subplots(figsize=(5.0, 3.2), dpi=100)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')
    
    if categories and stock_counts:
        bars = ax.bar(categories, stock_counts, color='#6366f1', width=0.5, edgecolor='#4338ca')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='#0f172a', fontsize=8, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No Inventory Data', color='#64748b', ha='center', va='center', fontsize=12)

    ax.set_title('Stock Quantity by Category', color='#0f172a', fontsize=12, pad=12, fontweight='bold')
    ax.tick_params(colors='#334155', labelsize=8)
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.spines['top'].set_color('#cbd5e1')
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['right'].set_color('#cbd5e1')
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#cbd5e1')
    plt.xticks(rotation=20)
    plt.tight_layout()
    return fig

def figure_to_base64(fig):
    """
    Converts Matplotlib Figure to Base64 encoded PNG string.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str
