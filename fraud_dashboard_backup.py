import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Fraud Framework Matrix",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Password protection function
def check_password():
    """Returns `True` if the user entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "fractal123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Return True if password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show password input
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 60vh;">
        <div style="text-align: center; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); background: white; max-width: 400px;">
            <h2 style="color: #1f77b4; margin-bottom: 1rem;">🔒 Fraud Framework Access</h2>
            <p style="color: #666; margin-bottom: 2rem;">Please enter the password to access the dashboard</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the password input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Enter password..."
        )
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😞 Password incorrect. Please try again.")
    
    return False


# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}
.matrix-button {
    border: 2px solid #ddd;
    border-radius: 15px;
    padding: 20px;
    margin: 5px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    font-size: 14px;
    line-height: 1.4;
}
.matrix-button:hover {
    border-color: #1f77b4;
    box-shadow: 0 6px 12px rgba(31, 119, 180, 0.2);
    transform: translateY(-2px);
}
.high-high {
    background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
    border-color: #4caf50;
}
.high-medium {
    background: linear-gradient(135deg, #fff3e0, #ffcc80);
    border-color: #ff9800;
}
.high-low {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    border-color: #f44336;
}
.medium-high {
    background: linear-gradient(135deg, #e3f2fd, #90caf9);
    border-color: #2196f3;
}
.medium-medium {
    background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
    border-color: #9e9e9e;
}
.medium-low {
    background: linear-gradient(135deg, #fce4ec, #f8bbd9);
    border-color: #e91e63;
}
.low-high {
    background: linear-gradient(135deg, #f3e5f5, #ce93d8);
    border-color: #9c27b0;
}
.low-medium {
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border-color: #ffc107;
}
.low-low {
    background: linear-gradient(135deg, #efebe9, #d7ccc8);
    border-color: #795548;
}
.scenario-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 5px solid #1f77b4;
}
.field-label {
    font-weight: bold;
    color: #1f77b4;
    margin-top: 15px;
    margin-bottom: 5px;
}
.field-value {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    border-left: 3px solid #dee2e6;
}
.metric-big {
    font-size: 2rem;
    font-weight: bold;
    color: #1f77b4;
}
.quadrant-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 10px;
}
.axis-label {
    font-weight: bold;
    color: #1f77b4;
    font-size: 16px;
}
.count-highlight {
    font-size: 24px;
    font-weight: bold;
    color: #1f77b4;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
div[data-testid="stButton"] > button {
    height: 140px;
    white-space: pre-line;
    font-size: 13px;
    line-height: 1.3;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the fraud framework data"""
    try:
        df = pd.read_csv('fraud_framework.csv')
        # Clean column names
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("Please ensure 'fraud_framework.csv' is in the same directory as this app.")
        return None

def create_matrix_data(df):
    """Create matrix data grouped by Business Value and Feasibility"""
    matrix_data = {}
    
    # Define the order for consistent display
    business_values = ['High', 'Medium']
    feasibilities = ['High', 'Medium', 'Low']
    
    for bv in business_values:
        for feas in feasibilities:
            key = f"{bv}-{feas}"
            filtered_data = df[(df['Business Value'] == bv) & (df['Feasibility'] == feas)]
            if len(filtered_data) > 0:
                matrix_data[key] = filtered_data
    
    return matrix_data

def get_quadrant_info(bv, feas):
    """Get quadrant information and styling"""
    quadrant_info = {
        'High-High': {
            'title': 'Quick Wins',
            'description': 'High Business Value & High Feasibility',
            'class': 'high-high',
            'icon': '🎯'
        },
        'High-Medium': {
            'title': 'Major Projects',
            'description': 'High Business Value & Medium Feasibility',
            'class': 'high-medium',
            'icon': '🚀'
        },
        'High-Low': {
            'title': 'Challenging',
            'description': 'High Business Value & Low Feasibility',
            'class': 'medium-low',
            'icon': '⛰️'
        },
        'Medium-High': {
            'title': 'Fill-ins',
            'description': 'Medium Business Value & High Feasibility',
            'class': 'medium-high',
            'icon': '🔧'
        },
        'Medium-Medium': {
            'title': 'Consider Carefully',
            'description': 'Medium Business Value & Medium Feasibility',
            'class': 'medium-medium',
            'icon': '🤔'
        },
        'Medium-Low': {
            'title': 'Questionable',
            'description': 'Medium Business Value & Low Feasibility',
            'class': 'medium-low',
            'icon': '⚠️'
        },
        'Low-High': {
            'title': 'Easy Wins',
            'description': 'Low Business Value & High Feasibility',
            'class': 'medium-high',
            'icon': '🎈'
        },
        'Low-Medium': {
            'title': 'Reconsider',
            'description': 'Low Business Value & Medium Feasibility',
            'class': 'medium-medium',
            'icon': '🔍'
        },
        'Low-Low': {
            'title': 'Avoid',
            'description': 'Low Business Value & Low Feasibility',
            'class': 'medium-low',
            'icon': '❌'
        }
    }
    
    key = f"{bv}-{feas}"
    return quadrant_info.get(key, {
        'title': 'Other',
        'description': f'{bv} Business Value & {feas} Feasibility',
        'class': 'medium-medium',
        'icon': '📋'
    })

def display_scenario_details(scenario_data):
    """Display detailed information for a scenario"""
    st.markdown(f"""
    <div class="scenario-card">
        <h3 style="color: #1f77b4; margin-top: 0;">{scenario_data['Scenario']}</h3>
        <h4 style="color: #666; margin-top: 5px;">Category: {scenario_data['Category']}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="field-label">🎯 Objective</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Objective"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">⚙️ Mechanic</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Mechanic"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">🔍 Important Aspects/Loopholes</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Important aspects/ loopholes"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">🚨 Detection Rule & Signal</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Detection Rule & Signal"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">📊 Must Have Data</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Must Have Data"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">🗃️ Data Fields</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{scenario_data["Data Fields"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">💰 Benefit to Costco</div>', unsafe_allow_html=True)
        benefit = scenario_data.get("Benefit to Costco (severity, frequency & Value)", "Not specified")
        st.markdown(f'<div class="field-value">{benefit}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">💼 Business Input on Practicality</div>', unsafe_allow_html=True)
        business_input = scenario_data.get("Input on praticality from Business", "Not specified")
        st.markdown(f'<div class="field-value">{business_input}</div>', unsafe_allow_html=True)
    
    with col2:
        # Assessment metrics
        st.markdown('<div class="field-label">💪 Effort Assessment</div>', unsafe_allow_html=True)
        effort_color = {'Low': '#4caf50', 'Medium': '#ff9800', 'High': '#f44336'}.get(scenario_data['Effort'], '#666')
        st.markdown(f'<div class="field-value"><span style="color: {effort_color}; font-weight: bold;">{scenario_data["Effort"]}</span><br><small>{scenario_data["Effort Reason"]}</small></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">🧩 Complexity Assessment</div>', unsafe_allow_html=True)
        complexity_color = {'Low': '#4caf50', 'Medium': '#ff9800', 'High': '#f44336'}.get(scenario_data['Complexity'], '#666')
        st.markdown(f'<div class="field-value"><span style="color: {complexity_color}; font-weight: bold;">{scenario_data["Complexity"]}</span><br><small>{scenario_data["Complexity Reason"]}</small></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">✅ Feasibility Assessment</div>', unsafe_allow_html=True)
        feasibility_color = {'Low': '#f44336', 'Medium': '#ff9800', 'High': '#4caf50'}.get(scenario_data['Feasibility'], '#666')
        st.markdown(f'<div class="field-value"><span style="color: {feasibility_color}; font-weight: bold;">{scenario_data["Feasibility"]}</span><br><small>{scenario_data["Feasibility Reason"]}</small></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">💎 Business Value Assessment</div>', unsafe_allow_html=True)
        bv_color = {'Low': '#f44336', 'Medium': '#ff9800', 'High': '#4caf50'}.get(scenario_data['Business Value'], '#666')
        st.markdown(f'<div class="field-value"><span style="color: {bv_color}; font-weight: bold;">{scenario_data["Business Value"]}</span><br><small>{scenario_data["Business Value Reason"]}</small></div>', unsafe_allow_html=True)

def main():
    # Check password first
    if not check_password():
        return
    
    # Add logout button in sidebar
    with st.sidebar:
        if st.button("🚪 Logout"):
            st.session_state["password_correct"] = False
            st.rerun()
    
    # Header
    st.markdown('<h1 class="main-header"> Fraud Framework Priority Matrix</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Create matrix data
    matrix_data = create_matrix_data(df)
    
    # Initialize session state for selected quadrant
    if 'selected_quadrant' not in st.session_state:
        st.session_state.selected_quadrant = None
    
    # Display matrix overview
    st.markdown("<h3 style='text-align: center;'> Priority Matrix - Click on any quadrant to explore scenarios in detail</h3>", unsafe_allow_html=True)
    
    # Create matrix header with axes labels
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <div style="margin-bottom: 20px; font-weight: bold; color: #1f77b4; font-size: 18px;">
            FEASIBILITY
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add column headers for feasibility
    header_col1, header_col2, header_col3, header_col4 = st.columns([0.25, 1, 1, 1])
    with header_col1:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; font-size: 16px; 
                    transform: rotate(-90deg); height: 80px; display: flex; align-items: center; 
                    justify-content: center; margin-top: 40px;'>
            BUSINESS VALUE
        </div>
        """, unsafe_allow_html=True)
    with header_col2:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 60px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            HIGH
        </div>
        """, unsafe_allow_html=True)
    with header_col3:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 60px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            MEDIUM
        </div>
        """, unsafe_allow_html=True)
    with header_col4:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 60px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            LOW
        </div>
        """, unsafe_allow_html=True)
    
    # Row 1: High Business Value
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns([0.25, 1, 1, 1])
    
    with row1_col1:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 140px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            HIGH
        </div>
        """, unsafe_allow_html=True)
    
    
    with row1_col2:
        quadrant = get_quadrant_info('High', 'High')
        count = len(matrix_data.get('High-High', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="high-high", help="High Business Value & High Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'High-High'
    
    with row1_col3:
        quadrant = get_quadrant_info('High', 'Medium')
        count = len(matrix_data.get('High-Medium', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="high-medium", help="High Business Value & Medium Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'High-Medium'
    
    with row1_col4:
        quadrant = get_quadrant_info('High', 'Low')
        count = len(matrix_data.get('High-Low', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="high-low", help="High Business Value & Low Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'High-Low'
    
    # Row 2: Medium Business Value
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns([0.25, 1, 1, 1])
    
    with row2_col1:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 140px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            MEDIUM
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        quadrant = get_quadrant_info('Medium', 'High')
        count = len(matrix_data.get('Medium-High', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="medium-high", help="Medium Business Value & High Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Medium-High'
    
    with row2_col3:
        quadrant = get_quadrant_info('Medium', 'Medium')
        count = len(matrix_data.get('Medium-Medium', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="medium-medium", help="Medium Business Value & Medium Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Medium-Medium'
    
    with row2_col4:
        quadrant = get_quadrant_info('Medium', 'Low')
        count = len(matrix_data.get('Medium-Low', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="medium-low", help="Medium Business Value & Low Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Medium-Low'
    
    # Row 3: Low Business Value (for completeness)
    row3_col1, row3_col2, row3_col3, row3_col4 = st.columns([0.25, 1, 1, 1])
    
    with row3_col1:
        st.markdown("""
        <div style='text-align: center; font-weight: bold; color: #1f77b4; 
                    height: 140px; display: flex; align-items: center; justify-content: center; 
                    font-size: 16px; background-color: #f8f9fa; border-radius: 8px; margin: 5px;'>
            LOW
        </div>
        """, unsafe_allow_html=True)
    
    with row3_col2:
        quadrant = get_quadrant_info('Low', 'High')
        count = len(matrix_data.get('Low-High', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="low-high", help="Low Business Value & High Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Low-High'
    
    with row3_col3:
        quadrant = get_quadrant_info('Low', 'Medium')
        count = len(matrix_data.get('Low-Medium', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="low-medium", help="Low Business Value & Medium Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Low-Medium'
    
    with row3_col4:
        quadrant = get_quadrant_info('Low', 'Low')
        count = len(matrix_data.get('Low-Low', []))
        button_text = f"{quadrant['icon']} **{quadrant['title']}**\n\n**{count}** scenarios\n\n{quadrant['description']}"
        if st.button(button_text, key="low-low", help="Low Business Value & Low Feasibility", use_container_width=True):
            st.session_state.selected_quadrant = 'Low-Low'
    
    # Display selected quadrant details
    if st.session_state.selected_quadrant:
        quadrant_data = matrix_data.get(st.session_state.selected_quadrant, pd.DataFrame())
        quadrant_info = get_quadrant_info(*st.session_state.selected_quadrant.split('-'))
        
        st.markdown("---")
        st.markdown(f"## {quadrant_info['icon']} {quadrant_info['title']} - {len(quadrant_data)} Scenarios")
        st.markdown(f"*{quadrant_info['description']}*")
        
        # Display scenarios if any exist
        if len(quadrant_data) > 0:
            # Display each scenario in the selected quadrant
            for idx, (_, scenario) in enumerate(quadrant_data.iterrows()):
                st.markdown(f"### Scenario {idx + 1}")
                display_scenario_details(scenario)
                st.markdown("---")
        else:
            # Display message when no scenarios exist
            st.info(f"No scenarios currently exist in the {quadrant_info['title']} quadrant.")
            st.markdown("### 💡 What this means:")
            
            bv, feas = st.session_state.selected_quadrant.split('-')
            if bv == 'High' and feas == 'Low':
                st.markdown("""
                This quadrant would contain scenarios with:
                - **High Business Value**: Significant impact on business operations
                - **Low Feasibility**: Difficult or challenging to implement
                
                These scenarios typically require substantial resources or face significant technical/operational barriers.
                """)
            elif bv == 'Low' and feas == 'High':
                st.markdown("""
                This quadrant would contain scenarios with:
                - **Low Business Value**: Limited impact on business operations  
                - **High Feasibility**: Easy to implement
                
                These scenarios are typically quick fixes but may not provide significant business benefit.
                """)
            elif bv == 'Low' and feas == 'Low':
                st.markdown("""
                This quadrant would contain scenarios with:
                - **Low Business Value**: Limited impact on business operations
                - **Low Feasibility**: Difficult to implement
                
                These scenarios are generally not recommended for implementation due to poor cost-benefit ratio.
                """)
            else:
                st.markdown(f"""
                This quadrant is for scenarios with **{bv} Business Value** and **{feas} Feasibility**.
                """)
        
        # Add a clear selection button at the bottom
        if st.button("🔙 Back to Matrix Overview"):
            st.session_state.selected_quadrant = None
            st.rerun()
    
    else:
        # Display summary statistics
        st.markdown("---")
        st.markdown("### 📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Scenarios", len(df))
        
        with col2:
            high_bv_count = len(df[df['Business Value'] == 'High'])
            st.metric("High Business Value", high_bv_count)
        
        with col3:
            high_feas_count = len(df[df['Feasibility'] == 'High'])
            st.metric("High Feasibility", high_feas_count)
        
        with col4:
            quick_wins = len(matrix_data.get('High-High', []))
            st.metric("Quick Wins", quick_wins)
        
        # Display matrix legend
        st.markdown("### 🗺️ Matrix Legend")
        legend_col1, legend_col2 = st.columns(2)
        
        with legend_col1:
            st.markdown("""
            **Quadrant Definitions:**
            - 🎯 **Quick Wins**: High value, easy to implement
            - 🚀 **Major Projects**: High value, moderate effort
            - 🔧 **Fill-ins**: Medium value, easy to implement
            """)
        
        with legend_col2:
            st.markdown("""
            **Assessment Criteria:**
            - 🤔 **Consider Carefully**: Medium value & feasibility
            - ⚠️ **Questionable**: Low feasibility scenarios
            - 📊 **Data-Driven**: All assessments include detailed reasoning
            """)

if __name__ == "__main__":
    main()