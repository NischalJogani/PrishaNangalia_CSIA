"""
Designer Budget Management Module
Handles budget overview and expense tracking
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record
from utils import format_currency, show_success, show_error, show_info, calculate_budget_statistics

def show_budget_overview():
    """
    Display budget overview interface
    Track estimated vs actual costs
    """
    st.header("💰 Budget Overview")
    
    project_id = st.session_state.get('active_project_id')
    if not project_id:
        show_info("Please select a project from Project Management first")
        return
    
    st.subheader(f"Project: {st.session_state.get('active_project_name', 'N/A')}")
    
    # Get all budget items
    budget_items = get_records('budget_items', 'project_id = %s', (project_id,))
    
    if budget_items:
        # Calculate statistics
        stats = calculate_budget_statistics(budget_items)
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Estimated", format_currency(stats['total_estimated']))
        with col2:
            st.metric("Total Actual", format_currency(stats['total_actual']))
        with col3:
            difference_color = "red" if stats['over_budget'] else "green"
            st.metric(
                "Difference", 
                format_currency(abs(stats['difference'])),
                delta=f"{'Over' if stats['over_budget'] else 'Under'} Budget",
                delta_color="inverse" if stats['over_budget'] else "normal"
            )
        
        st.divider()
        
        # Display and edit budget items
        st.subheader("📊 Budget Items")
        
        for item in budget_items:
            with st.expander(f"💵 {item['item_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    estimated = st.number_input(
                        "Estimated Cost (₹)",
                        min_value=0.0,
                        value=float(item['estimated_cost']),
                        step=1000.0,
                        key=f"est_{item['id']}"
                    )
                
                with col2:
                    actual = st.number_input(
                        "Actual Cost (₹)",
                        min_value=0.0,
                        value=float(item['actual_cost']),
                        step=1000.0,
                        key=f"act_{item['id']}"
                    )
                
                col_save, col_delete = st.columns(2)
                
                with col_save:
                    if st.button("💾 Save", key=f"save_budget_{item['id']}"):
                        update_data = {
                            'estimated_cost': estimated,
                            'actual_cost': actual
                        }
                        update_record('budget_items', update_data, 'id = %s', (item['id'],))
                        show_success("Budget item updated!")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"del_budget_{item['id']}"):
                        delete_record('budget_items', 'id = %s', (item['id'],))
                        show_success("Budget item deleted!")
                        st.rerun()
        
        st.divider()
    
    # Add new budget item
    st.subheader("➕ Add New Budget Item")
    
    with st.form("add_budget_item"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_name = st.text_input("Item Name", placeholder="e.g., Sofa Set")
        with col2:
            estimated_cost = st.number_input("Estimated Cost (₹)", min_value=0.0, step=1000.0)
        with col3:
            actual_cost = st.number_input("Actual Cost (₹)", min_value=0.0, step=1000.0)
        
        submit = st.form_submit_button("Add Budget Item", type="primary")
        
        if submit and item_name:
            budget_data = {
                'project_id': project_id,
                'item_name': item_name,
                'estimated_cost': estimated_cost,
                'actual_cost': actual_cost
            }
            insert_record('budget_items', budget_data)
            show_success("Budget item added successfully!")
            st.rerun()
