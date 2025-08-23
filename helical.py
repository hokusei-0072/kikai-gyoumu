import streamlit as st

st.title("ヘリカル加工プログラム")# タイトル

#### 変数の仮定義 ####
KH = 0
ZHOSEI = 0

#### 入力フォーム ####
filename = st.text_input("プログラムの名前を入力")
D = st.text_input("工具径",placeholder="例 9.8Φエンドミルなら9.8と入力")
S = st.text_input("回転数",value=800)
F = st.text_input("送り",value=200)
Z = st.text_input("加工深さ",placeholder=20)
CHEK = st.checkbox("Z方向の仕上しろ")
if CHEK:
    ZHOSEI = st.text_input("Zの仕上しろ",value=0.2)
ZP = st.text_input("Zピッチ",value=0.5)
KD = st.text_input("穴径",placeholder="加工したい穴の径を入力")
HOSEI = st.text_input("仕上しろ",placeholder="-0.01 , 0.1")
NZ = st.text_input("Zの逃げ量",value=200)

#### ボタン ####
BUTTON = st.button("計算")
if BUTTON:
    #### 変数定義　計算　####
    KZHOSEI = ZHOSEI
    KHOSEI = HOSEI
    d = float(D) / 2  # 工具半径を求める。
    if HOSEI != '': # 仕上げしろに数値が入力されているなら処理開始
        if "-" in HOSEI:
            KH = HOSEI.replace('-', '')# リプレイスを使って-を削除
            KH = float(KH)# -を削除して残った数値(str)をfloatに変換
            d = d - KH #工具半径－仕上げしろで補正値込みの工具半径を求める(追い込み)
        else:
            KH = float(HOSEI) # strをfloatに変換
            d = d + KH #工具半径＋仕上げしろで補正値込みの工具半径を求める(削り残し)

    Q = float(Z) // float(ZP)# 加工深さを余り無しで割り算＝コピーの回数。
    r = float(Z) % float(ZP)# 余りだけを計算。
    #Q,R = float(Z) // float(ZP), float(Z) % float(ZP) #上の計算をまとめて処理する場合。
    r = round(r,3)# 小数点第3位までに変換。
    Q = int(Q)
    R = float(ZP) - r# Zピッチ(ZP)から加工深さの余り(r)を引いて加工開始Zを求める。
    R = round(R,3)# 加工開始Zを小数点第３位までに変換。
    YJ = (float(KD) / 2) - d# 加工したい穴の半径から工具半径を引いてYとJの値を求める。
    YJ = round(YJ,3)# YとJの値を小数点第３位までに変換。
    KZ = float(ZP) * Q + r# 加工深さの確認用の変数、Zピッチ(ZP)×コピー回数(Q)＋割り切れなかった余りの加工深さ(r)= 実際の加工深さ(KZ)
    K_YJ = (YJ * 2) + float(D) # 加工径確認用の変数
    K_YJ = round(K_YJ,3)
    KZHOSEI = float(KZHOSEI)
    KZHOSEI = round(KZHOSEI,3)
    KZ = KZ - KZHOSEI
    KZ = round(KZ,3)
    #### プログラム作成部分 ####
    program_ka =  f"(工具径{D}Φ)\n(仕上げしろ{KHOSEI})(Z仕上しろ{KZHOSEI})\n(加工径{K_YJ}Φ)(加工深さ{KZ}mm)\n"
    program1 = f"S{S}M3\nM12\nG56Z{NZ}H01\nMODIN O2\nCALL O1\nMODOUT\nG00Z{NZ}\nM09\nM05\nM02\nO1\n(座標を貼り付け)\nRTS"
    if CHEK:
        if r == 0.0:
            program2 = f"O2\nZ5\nG01Z0+{ZHOSEI}F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS"
        else:
            program2 = f"O2\nZ5\nG01Z{R}+{ZHOSEI}F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS"
    else :
        if r == 0.0:
            program2 = f"O2\nZ5\nG01Z0F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS"
        else:
            program2 = f"O2\nZ5\nG01Z{R}F50\nG91G41Y-{YJ}D01F{F}\nCALL O3 Q{Q}\nG03J{YJ}F{F}\nG01G40Y{YJ}\nG90G00Z{NZ}\nRTS"
    program3 = f"O3\nG91G03J{YJ}Z-{ZP}F{F}\nRTS"

    program_date = "\n".join([program_ka, program1, program2, program3]) # 作成したプログラムを改行付きで結合

    st.download_button(
        label=f"{filename}.MINをダウンロード",
        data=program_date.encode("shift_jis"),
        file_name=f"{filename}.MIN",
        mime="text/plain"
    )

    #### プログラム表示部分 ####
    st.text(program_date)

    #### 動作確認用 ####
    # st.text(f"コピー回数{Q}")
    # st.text(f"加工開始{R}")
    # st.text(f"Y,J{YJ}")
    # st.text(f"{r}")
    # st.text(f"径補正{KH}")
    # st.text(f"補正後の工具半径{d}")
