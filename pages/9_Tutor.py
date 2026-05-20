import streamlit as st
from core.ai import tutor_chat

st.set_page_config(page_title="Trading Tutor", page_icon="🎓", layout="wide")
st.title("🎓 AI Trading Tutor")
st.caption("Ask anything about trading, crypto, stocks, or investing. No judgment — this is your personal learning space.")

groq_key = st.session_state.get("groq_api_key", "")
if not groq_key:
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

if not groq_key:
    st.warning("Add your Groq API key in the Checklist sidebar to use the tutor.")
    st.stop()

# Suggested questions for beginners
with st.expander("💡 Not sure what to ask? Try these"):
    suggestions = [
        "What is a stop loss and why is it so important?",
        "What does RSI mean and how do I use it?",
        "Why do most beginners lose money in crypto?",
        "What is the difference between a bull and bear market?",
        "How much of my money should I risk per trade?",
        "What is FOMO and how does it make traders lose money?",
        "What is support and resistance?",
        "What is dollar-cost averaging (DCA)?",
        "How do I know when NOT to trade?",
        "What is market cap and why does it matter?",
    ]
    cols = st.columns(2)
    for i, q in enumerate(suggestions):
        if cols[i % 2].button(q, key=f"sug_{i}", use_container_width=True):
            st.session_state.setdefault("tutor_messages", [])
            st.session_state["tutor_messages"].append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                try:
                    reply = tutor_chat(groq_key, st.session_state["tutor_messages"])
                    st.session_state["tutor_messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

st.markdown("---")

# Chat history
if "tutor_messages" not in st.session_state:
    st.session_state["tutor_messages"] = []

for msg in st.session_state["tutor_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask your trading question..."):
    st.session_state["tutor_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = tutor_chat(groq_key, st.session_state["tutor_messages"])
                st.session_state["tutor_messages"].append({"role": "assistant", "content": reply})
                st.markdown(reply)
            except Exception as e:
                msg = str(e)
                if "auth" in msg.lower() or "401" in msg:
                    st.error("Invalid Groq API key.")
                else:
                    st.error(f"Error: {msg}")

if st.session_state.get("tutor_messages"):
    if st.button("🗑️ Clear chat", type="secondary"):
        st.session_state["tutor_messages"] = []
        st.rerun()
