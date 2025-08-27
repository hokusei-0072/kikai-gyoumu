import streamlit as st

### タイトル ###
st.title("U溝加工プログラム")

### 変数仮定義 ###
P_KAZU_LIST = []
M_KAZU_LIST = []
P_U_ZAHYOU_LIST = []
M_U_ZAHYOU_LIST = []

### 入力フォーム ###
### ファイル名入力
program_name = st.text_input("プログラムの名前を入力")

### 加工方向の選択
HOUKOU = st.selectbox("加工方向を選択",("X方向","Y方向"))
if HOUKOU == "X方向":
    HOUKOU = "X"
    HOUKOU2 = "Y"
else:
    HOUKOU = "Y"
    HOUKOU2 = "X"

### U溝の数を選択
P_KAZU = st.selectbox(f"{HOUKOU}プラス側のU溝の数を選択",(2,3,4,5,6,7,8))
for i in range(P_KAZU):
    P_K = 1 + i
    P_KAZU_LIST.append(P_K)
KAZU_MIRROR = st.checkbox(f"{HOUKOU}マイナス側の数は対称ではない")
if KAZU_MIRROR:
    M_KAZU = st.selectbox(f"{HOUKOU}マイナス側のU溝の数を選択",(2,3,4,5,6,7,8))
    for i in range(M_KAZU):
        M_K = 1 + i
        M_KAZU_LIST.append(M_K)
else:
    M_KAZU = P_KAZU
    M_KAZU_LIST = P_KAZU_LIST

### U溝の中心座標の入力
for i in P_KAZU_LIST:
    P_U_ZAHYOU = st.text_input(f"{HOUKOU}プラス側U溝中心の座標{i}を入力({HOUKOU2}座標)")
    P_U_ZAHYOU_LIST.append(P_U_ZAHYOU)

ZAHYOU_MIRROR = st.checkbox(f"{HOUKOU}マイナス側の座標は対称ではない")
if ZAHYOU_MIRROR:
    for i in M_KAZU_LIST:
        M_U_ZAHYOU = st.text_input(f"{HOUKOU}マイナス側U溝中心の座標{i}を入力({HOUKOU2}座標)")
        M_U_ZAHYOU_LIST.append(M_U_ZAHYOU)
else:
    M_U_ZAHYOU_LIST = P_U_ZAHYOU_LIST

### U溝の加工終了位置の入力
P_U_ZAHYOU_END = st.text_input(f"{HOUKOU}プラス側U溝中心の座標を入力({HOUKOU}座標)")
P_U_ZAHYOU_END_MIRROR = st.checkbox("対称ではない")
if P_U_ZAHYOU_END_MIRROR:
    M_U_ZAHYOU_END = st.text_input(f"{HOUKOU}マイナス側U溝中心の座標を入力({HOUKOU}座標)")
else:
    M_U_ZAHYOU_END = P_U_ZAHYOU_END


### 鋳物の端面を入力
P_TANMEN = st.text_input(f"{HOUKOU}プラス側鋳物端面の座標を入力")
TANMEN_MIRROR = st.checkbox("マイナス側端面は対称ではない")
if TANMEN_MIRROR:
    M_TANMEN = st.text_input(f"{HOUKOU}マイナス側鋳物端面の座標を入力")
else:
    M_TANMEN = P_TANMEN

### 削りしろの入力
UMIZO_Z = st.text_input("U溝削りしろ",value=6)
UMIZO_Z = int(UMIZO_Z)

### 加工ピッチ
zp = st.text_input("Z方向の加工ピッチ",value=2)
ZP = int(zp)

### zの逃げ量
NZ = st.text_input("Zの逃げ量",value=200)

### ボタン
KEISAN_B = st.button("プログラム作成")

### プログラム作成 ###
if KEISAN_B:
    # コピー回数の計算
    Q = (UMIZO_Z / ZP) + 1
    Q = int(Q)

    # スタート点の計算とマイナス側のミラー処理
    if TANMEN_MIRROR:
        P_TANMEN = int(P_TANMEN)
        P_START = P_TANMEN + 85
        M_TANMEN = int(M_TANMEN)
        M_START = M_TANMEN - 85
        M_START = str(M_START)
        M_START = M_START.replace("-","")
    else:
        P_TANMEN = int(P_TANMEN)
        P_START = P_TANMEN + 85
        M_TANMEN = int(M_TANMEN)
        M_START = M_TANMEN + 85

    if P_U_ZAHYOU_END_MIRROR:
        M_U_ZAHYOU_END = M_U_ZAHYOU_END.replace("-","")



    # 確認用データ
    KA_program = "(U溝位置確認用)\nG90G00X0Y0\n"
    for i,j in enumerate(P_U_ZAHYOU_LIST):
        KA_program += f"{HOUKOU}{P_START}{HOUKOU2}{j}\n"
    for i, j in enumerate(M_U_ZAHYOU_LIST):
        KA_program += f"{HOUKOU}-{M_START}{HOUKOU2}{j}\n"

    # 加工開始前のセットアップ部分
    program1 = f"\n\n(ここから加工開始)\nM00\nG90G00Z{NZ}\nX0Y0\nVC1=-{UMIZO_Z}.2\nS500M3\nM12\nCOPY Q{Q}\n"

    # ここから加工スタート
    program2 = ""
    for i,j in enumerate(P_U_ZAHYOU_LIST):
        program2 += (f"G90G00{HOUKOU}{P_START}{HOUKOU2}{j}\nZ=VC1+5\nG01Z=VC1F500\n"
                     f"{HOUKOU}{P_U_ZAHYOU_END}F500\n{HOUKOU}{P_START}F1000\nG00Z{NZ}\n")

    for i, j in enumerate(M_U_ZAHYOU_LIST):
        program2 += (f"G90G00{HOUKOU}-{M_START}{HOUKOU2}{j}\nZ=VC1+5\nG01Z=VC1F500\n"
                     f"{HOUKOU}-{M_U_ZAHYOU_END}F500\n{HOUKOU}-{M_START}F1000\nG00Z{NZ}\n")

    # コピー終了後に仕上げ加工
    program3 = f"VC1=VC1+{ZP}\nCOPYE\n\n(仕上げ加工)\nVC1=0\n{program2}M09\nM05\nM02"

    DATE = "\n".join([KA_program,program1,program2,program3])

    ### ダウンロードボタン
    st.download_button(
        label=f"{program_name}.MINをダウンロード",
        data=DATE.encode("shift_jis"),  # ← ここがポイント！
        file_name=f"{program_name}.MIN",
        mime="text/plain"
    )

    ### プログラム表示 ###
    st.text(DATE)


### 動作確認用 ###
# st.text(P_KAZU_LIST)
# st.text(M_KAZU_LIST)
# st.text(P_U_ZAHYOU_LIST)
# st.text(M_U_ZAHYOU_LIST)
