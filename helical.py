import streamlit as st

st.title("ヘリカル加工プログラム")# タイトル

#### 入力フォーム ####
D = st.text_input("工具径",placeholder="例 9.8Φエンドミルなら9.8と入力")#
S = st.text_input("回転数",value=800)#
F = st.text_input("送り",value=200)#
Z = st.text_input("加工深さ",placeholder=20)
ZP = st.text_input("Zピッチ",value=0.5)
KD = st.text_input("穴径",placeholder="加工したい穴の径を入力")
NZ = st.text_input("Zの逃げ量",value=200)#

BUTTON = st.button("計算")
if BUTTON:
    #### 変数定義　計算　####
    Q = float(Z) // float(ZP)# 加工深さを余り無しで割り算＝コピーの回数
    r = float(Z) % float(ZP)# 余りだけを計算
    #Q,R = float(Z) // float(ZP), float(Z) % float(ZP) #上の計算をまとめて処理する場合
    r = round(r,3) # 小数点第３位までに変換
    Q = int(Q)# 整数に変換
    R = float(ZP) - r# Zピッチ-割り切れない余り＝加工開始点
    R = round(R,3)# 小数点第３位までに変換
    d = float(D) / 2# 工具径の半径
    YJ = (float(KD) / 2) - d# 加工径の半径-工具の半径＝加工パス
    YJ = round(YJ,3)# 小数点第３位までに変換
    KZ = float(ZP) * Q + r# 加工深さの確認用

    #### プログラム表示部分 ####
    st.text(f"(工具径{D}Φ)\n(加工径{KD}Φ)\n(加工深さ{KZ})mm")
    st.text(f"S{S}M3\nM12\nG56Z{NZ}H01\n")
    st.text(f"MODIN O2\nCALL O1\nMODOUT\nG00Z{NZ}\nM09\nM05\nM02")
    st.text("O1\n(座標を貼り付け)\nRTS")
    if r == 0.0:
        st.text(f"O2\nZ5\nG01Z0F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS")
    else:
        st.text(f"O2\nZ5\nG01Z{R}F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS")

    st.text(f"O3\nG91G03J{YJ}Z-{ZP}F{F}\nRTS")
    #### 確認 ####
    #st.text(f"コピー回数{Q}")
    #st.text(f"加工開始{R}")
    #st.text(f"Y,J{YJ}")
    #st.text(f"{r}")
