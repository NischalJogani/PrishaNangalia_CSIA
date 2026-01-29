"""
Designer Suppliers Management Module
Handles supplier contact information and search
"""

import streamlit as st
from database import insert_record, get_records, update_record, delete_record
from utils import show_success, show_error, show_info

def show_suppliers_management():
    """
    Display suppliers management interface
    Add, search, and manage supplier contacts
    """
    st.header("📦 Materials & Suppliers")
    
    # Search bar
    st.subheader("🔍 Search Suppliers")
    search_term = st.text_input("Search by name, category, or contact", placeholder="Enter search term...")
    
    # Get all suppliers
    if search_term:
        # Search in name, category, phone, email
        suppliers = get_records('suppliers', 
                               'name LIKE %s OR category LIKE %s OR phone LIKE %s OR email LIKE %s',
                               (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    else:
        suppliers = get_records('suppliers')
    
    # Display suppliers
    if suppliers:
        st.subheader(f"📋 Suppliers ({len(suppliers)} found)")
        
        # Group by category
        categories = {}
        for supplier in suppliers:
            cat = supplier.get('category', 'Uncategorized')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(supplier)
        
        # Display by category
        for category, supplier_list in categories.items():
            with st.expander(f"📁 {category} ({len(supplier_list)} suppliers)"):
                for supplier in supplier_list:
                    st.markdown(f"### {supplier['name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**📞 Phone:** {supplier['phone'] or 'N/A'}")
                        st.write(f"**📧 Email:** {supplier['email'] or 'N/A'}")
                    with col2:
                        st.write(f"**🏷️ Category:** {supplier['category'] or 'N/A'}")
                        st.write(f"**📍 Address:** {supplier['address'] or 'N/A'}")
                    
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_sup_{supplier['id']}"):
                            st.session_state[f'edit_supplier_{supplier["id"]}'] = True
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"del_sup_{supplier['id']}"):
                            delete_record('suppliers', 'id = %s', (supplier['id'],))
                            show_success("Supplier deleted!")
                            st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f'edit_supplier_{supplier["id"]}'):
                        with st.form(f"edit_supplier_form_{supplier['id']}"):
                            st.write("**Edit Supplier**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Name", value=supplier['name'])
                                new_category = st.text_input("Category", value=supplier['category'] or '')
                                new_phone = st.text_input("Phone", value=supplier['phone'] or '')
                            with col2:
                                new_email = st.text_input("Email", value=supplier['email'] or '')
                                new_address = st.text_area("Address", value=supplier['address'] or '')
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save = st.form_submit_button("💾 Save Changes")
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if save:
                                update_data = {
                                    'name': new_name,
                                    'category': new_category,
                                    'phone': new_phone,
                                    'email': new_email,
                                    'address': new_address
                                }
                                update_record('suppliers', update_data, 'id = %s', (supplier['id'],))
                                del st.session_state[f'edit_supplier_{supplier["id"]}']
                                show_success("Supplier updated!")
                                st.rerun()
                            
                            if cancel:
                                del st.session_state[f'edit_supplier_{supplier["id"]}']
                                st.rerun()
                    
                    st.divider()
    else:
        show_info("No suppliers found. Add some below!")
    
    st.divider()
    
    # Add new supplier
    st.subheader("➕ Add New Supplier")
    
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Supplier Name*", placeholder="ABC Furniture Co.")
            category = st.selectbox("Category", 
                                   ["Furniture", "Lighting", "Paint", "Flooring", 
                                    "Electricals", "Plumbing", "Fabrics", "Accessories", "Other"])
            phone = st.text_input("Phone", placeholder="+91 XXXXXXXXXX")
        
        with col2:
            email = st.text_input("Email", placeholder="supplier@example.com")
            address = st.text_area("Address", placeholder="Full address...")
        
        submit = st.form_submit_button("Add Supplier", type="primary")
        
        if submit:
            if not name:
                show_error("Please enter supplier name")
            else:
                supplier_data = {
                    'name': name,
                    'category': category,
                    'phone': phone,
                    'email': email,
                    'address': address
                }
                insert_record('suppliers', supplier_data)
                show_success("Supplier added successfully!")
                st.rerun()
