"""Display answers and their original evidence without executing document markup."""
import streamlit as st


def render_result(result):
    st.badge(result["route"], color="blue")
    st.caption(result.get("reason", ""))
    for warning in result["errors"]:
        st.warning(warning)
    if result.get("generation_method") == "evidence":
        st.info("Showing original evidence. A generated interpretation is unavailable or disabled.")
        st.text(result["answer"])
    else:
        st.markdown(result["answer"])
    if result["sources"]:
        with st.expander("Sources", expanded=False):
            for source in result["sources"]:
                location = source.get("source", source.get("source_file", ""))
                page = f" · page {source['page']}" if "page" in source else ""
                st.text(f"{source['tag']} {location}{page}")
    if result["evidence"]["sql"]:
        with st.expander("SQL evidence"):
            for item in result["evidence"]["sql"]:
                st.caption(f"{item['tag']} {item['source']}")
                st.dataframe(item["rows"], hide_index=True, width="stretch")
    if result["evidence"]["docs"]:
        with st.expander("Document evidence"):
            for item in result["evidence"]["docs"]:
                st.caption(f"{item['tag']} {item['source_file']} · page {item['page']} · similarity {item['score']:.3f}")
                if item.get("published_at"):
                    st.caption(f"Published: {item['published_at']}")
                st.text(item["text"])
    st.caption(f"Response time: {result['timings']['total_ms'] / 1000:.2f} s · {result.get('method', 'rules')} routing")
