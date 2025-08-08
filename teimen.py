import streamlit as st

st.title("底面プログラム")# タイトル

D = st.text_input("工具径",placeholder="例 125Φの高送りなら125と入力")
# テキストインプットを使って数字を入力してもらう。(.text_inputで入力される値は数字でも文字列(str)扱いになる)
# 最初に記述した文字列は入力フォームの説明文としてフォームの上に表示される＝ラベル
S = st.text_input("回転数",placeholder="500")
# ラベル＋カンマ＋プレースホルダーを使うとフォーム内に薄文字で入力例などを表示できる
F = st.text_input("送り",placeholder="4000")
Z = st.text_input("加工深さ",placeholder="5.5")
ZP = st.text_input("Zピッチ",placeholder="0.5")
XW = st.text_input("X寸法",placeholder="Xの幅を入力")
YW = st.text_input("Y寸法",placeholder="Yの幅を入力")

# st.buttonでボタンを作成できる、入力が完了した後に押してもらうことでその後の処理を開始したりするのに利用できる。
B = st.button("計算")# ボタンもラベルをつけて表示できる
# ボタンの状態を変数に代入して処理の実行や分岐に使用できる。ボタンが押されていない場合Bにはfalsが代入されている
if B:# "計算"ボタンが押された時にBにはtrueが代入されるのでif文の処理が実行される。
    XWp = int(XW) / 2 + int(D)# X0を設定するための座標
    YWm = int(YW) / 2 - int(YW)# Y0を設定するための座標
    XE = int(XWp) - (int(XWp) * 3)  # Xの加工終了の位置(X-の座標)
    DP = int(D) - 20# パスのステップ幅を計算(工具系ー20(ラップ量))
    CQ = float(Z) / float(ZP) + 1
    YW = int(YW)
    YWa = YW + (int(D) / 2)
    Ds = int(D) / 2 -15
    YWb = YWa - 15
    YP = 0
    P = []
    while YP < YW:
        YP += int(DP)
        P.append(YP)
    st.text(f"G90G00X{XWp}Y{YWm}(この位置で原点設定X0Y0)\nM00")
    st.text(f"VC1=0.2\n{S}M3\nM12\nCOPY Q{int(CQ)}\nG90G00X0Y0\nZ50\nZ=VC1+5\nG01Z=VC1F{F}\n"
            f"X{XE}F{F}\nG00Z50\n")
    for i,Yp in enumerate(P[:-1],start=1):
        st.text(f"X0Y0+{Yp}\nZ=VC1+5\nG01Z=VC1F{F}\nX{XE}F{F}\nG00Z50\n")
    if P[-2] + Ds >= YW:
        st.text(f"VC1=VC1-{ZP}\nCOPYE\nM09\nM05\nM02")
    else:
        st.text(f"X0Y0+{YW}\nZ=VC1+5\nG01Z=VC1F{F}\nX{XE}F{F}\nG00Z50\n")
        st.text(f"VC1=VC1-{ZP}\nCOPYE\nM09\nM05\nM02")

