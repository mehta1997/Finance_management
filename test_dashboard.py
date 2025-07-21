import streamlit as st

st.title("🚀 FinanceFlow Test Dashboard")
st.write("If you can see this, Streamlit is working!")

if st.button("Test Button"):
    st.success("Button clicked successfully!")

st.markdown("---")
st.write("API Status: Testing connection to http://localhost:8000")

try:
    import requests
    response = requests.get("http://localhost:8000", timeout=5)
    if response.status_code == 200:
        st.success("✅ API Connection Successful!")
        st.json(response.json())
    else:
        st.error(f"❌ API returned status code: {response.status_code}")
except Exception as e:
    st.error(f"❌ Cannot connect to API: {str(e)}")
    st.info("Make sure the API server is running on http://localhost:8000")
