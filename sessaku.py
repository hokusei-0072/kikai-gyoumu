import streamlit as st

st.title('切削条件計算')
st.text("Dに工具の直径、Zに工具の刃数、vcに切削速度、vfに１刃あたりの送りを入力")

D = st.text_input("工具径")
Z = st.text_input("刃数")
vc = st.text_input("切削速度")
vf = st.text_input("１刃あたりの送り")
s = st.text_input("回転数")
f = st.text_input("送り")

B = st.button("計算")
BB = st.button("切削速度を計算")

if B:
    S = float(vc) * 1000 / 3.14 / float(D)
    F = int(S) * int(Z) * float(vf)
    st.markdown(f"# 回転数 S= {int(S)}")
    st.markdown(f"# 送り F= {int(F)}")

if BB:
    VC = int(s) / 1000 * 3.14 * int(D)
    VF = int(f) / int(Z) / int(s)
    st.markdown(f"# 切削速度 vc= {round(VC,1)}")
    st.markdown(f"# 1刃あたりの送り vf= {round(VF,2)}")