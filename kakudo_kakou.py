import streamlit as st
import math

st.title("斜面切削プログラム")

### 入力フォーム

# ファイル名を入力
file_name = st.text_input("プログラム名を入力")

# 加工方向の選択
HOUKOU = st.selectbox("加工方向の選択",["X方向","Y方向"])
if HOUKOU == "X方向":
    HOUKOU = "X"
    HOUKOU2 = "Y"
else:
    HOUKOU = "Y"
    HOUKOU2 = "X"

# 斜面がプラス側かマイナス側か選択
PorM = st.selectbox(f"斜面の方向を選択({HOUKOU2}+側に斜面,{HOUKOU2}-側に斜面)",["＋側","-側"])
if PorM == "＋側":
    PorM = "+"
else:
    PorM = "-"

# 角度の入力
KakouKakudo = st.text_input("加工したい角度を入力",placeholder="30度の斜面なら30と入力")

# 底辺までの高さを入力
KakouTakasa = st.text_input("頂点から底辺までの高さを入力")

# 加工ピッチの入力
Pitch = st.text_input("加工ピッチを入力",value=0.5)

# スタート点
s1 = st.text_input(f"スタート点の座標({HOUKOU}座標)")
s2 = st.text_input(f"スタート点の座標({HOUKOU2}座標)")
sZ = st.text_input(f"スタート点の座標(Z座標)")

# エンド点
End = st.text_input(f"エンド点の座標({HOUKOU}座標)")

# 逃げ量
NZ = st.text_input("Zの逃げ量",value=100)

# プログラム作成ボタン
P_Button = st.button("プログラム作成")

# プログラム作成開始
if P_Button:
    # 計算
    sZ = float(sZ)
    sZ = round(sZ,3)
    H = float(KakouTakasa)
    Pitch = float(Pitch)

    # 角度を計算用に変換
    Tan = float(KakouKakudo)
    TAN = math.radians(Tan)

    # 底辺を計算
    K_Pitch = Pitch * math.tan(TAN)
    K_Pitch = round(K_Pitch,3)

    Q = (H // Pitch) + 1
    Q = int(Q)
    r = H % Pitch
    r = round(r,3)
    R = sZ + r
    R = round(R,3)

    program1 = f"VC1={R}\nVC2=0\nG90G00X0Y0\nZ200\nS1000M3\nM12\nCOPY Q{Q}"

    program2 = (f"G90G00{HOUKOU}{s1}{HOUKOU2}{s2}{PorM}VC2\nZ=VC1+5\nG01Z=VC1F50\n{HOUKOU}{End}F1000\n"
                f"G00Z{NZ}\nVC1=VC1-{Pitch}\nVC2=VC2{PorM}{K_Pitch}\nCOPYE\nM09\nM05\nM02")

    DATE = "\n".join([program1, program2])

    # ダウンロードボタン
    st.download_button(
        label=f"{file_name}.MINをダウンロード",
        data=DATE.encode("shift_jis"),
        file_name=f"{file_name}.MIN",
        mime="text/plain"
    )

    # 動作確認用
    st.text(f"高さ{H}")
    st.text(f"角度{Tan}")
    st.text(f"{HOUKOU2}ピッチ{K_Pitch}")
    st.text(f"余り{r}")
    st.text(f"加工開始Z{R}")

    # プログラム表示
    st.text(DATE)
