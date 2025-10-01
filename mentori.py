import streamlit as st

# タイトル
st.title("面取り加工プログラム")

### 入力フォーム ###
# ファイル名を入力
FILE_NAME = st.text_input("プログラムの名前を入力")

# 加工方向の選択
HOUKOU = st.selectbox("面取り方向の選択",["X方向","Y方向"])
if HOUKOU == "X方向":
    HOUKOU = "X"
    HOUKOU2 = "Y"
else:
    HOUKOU = "Y"
    HOUKOU2 = "X"

# 進行方向の選択
KAKOUHOUKOU = st.selectbox("加工方向の選択",["+方向","-方向"])

# スタート点の座標
S1 = st.text_input(f"スタート点({HOUKOU}座標)")
S2 = st.text_input(f"スタート点({HOUKOU2}座標)")
SZ = st.text_input("スタート点(Z座標)")

# エンド点の座標
E1 = st.text_input("加工距離",value=200)
E2 = st.text_input(f"エンド点({HOUKOU2}座標)")
EZ = st.text_input("エンド点(Z座標)")

# 加工ピッチの入力
KAKOU_P = st.text_input("加工ピッチを入力",value=0.5)

# Zの逃げ量
NZ = st.text_input("Zの逃げ量",value=100)

# 往復加工チェックボックス
OUHUKU = st.checkbox("往復加工")

# 計算ボタン
KEISAN = st.button("プログラム作成")
if KEISAN:
    E1 = int(E1)
    KAKOU_P = float(KAKOU_P)
    if OUHUKU:
        OUHUKU_P = KAKOU_P + KAKOU_P
        Q = E1 // OUHUKU_P
        Q = int(Q)
        EQ = E1 % KAKOU_P
    else:
        Q = E1 // KAKOU_P
        Q = int(Q)
        EQ = E1 % KAKOU_P

    # プログラム作成
    program1 = f"G90G00X0Y0\nS1000M3\nM12\n{HOUKOU}{S1}{HOUKOU2}{S2}\nZ{SZ}\nCOPY Q{Q}\n"

    if OUHUKU:
        program2 = (f"G91G01{HOUKOU}{KAKOUHOUKOU}{KAKOU_P}F50\nG90{HOUKOU2}{E2}Z{EZ}F500\nG91{HOUKOU}{KAKOUHOUKOU}{KAKOU_P}F50\n"
                    f"G90{HOUKOU2}{S2}Z{SZ}F500\nCOPYE\nM09\nM05\nM02\n")
    else:
        program2 = (f"G91G01{HOUKOU}{KAKOUHOUKOU}{KAKOU_P}F50\nG90{HOUKOU2}{E2}Z{EZ}F500\nG00Z{NZ}\n"
                    f"{HOUKOU2}{S2}\nZ{SZ}\nCOPYE\nM09\nM05\nM02\n")

    DATE = "\n".join([program1, program2])

    # ダウンロードボタン
    st.download_button(
        label=f"{FILE_NAME}.MINをダウンロード",
        data=DATE.encode("shift_jis"),
        file_name=f"{FILE_NAME}.MIN",
        mime="text/plain"
    )

    # プログラム表示
    st.text(DATE)

