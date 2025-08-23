import streamlit as st

st.title("底面プログラム")  # タイトル

filename = st.text_input("保存するファイル名を入力",placeholder="TEIMEN")
D = st.text_input("工具径", value=125)
# テキストインプットを使って数字を入力してもらう。(.text_inputで入力される値は数字でも文字列(str)扱いになる)
# 最初に記述した文字列は入力フォームの説明文としてフォームの上に表示される＝ラベル
S = st.text_input("回転数", value=500)
# ラベル＋カンマ＋プレースホルダーを使うとフォーム内に薄文字で入力例などを表示できる
F = st.text_input("送り", value=6000)
Z = st.text_input("加工深さ", placeholder="5.5")
ZP = st.text_input("Zピッチ", value=0.5)
XW = st.text_input("X寸法", placeholder="Xの幅を入力")
YW = st.text_input("Y寸法", placeholder="Yの幅を入力")
DS = st.text_input("仕上工具径", value=200)

# st.buttonでボタンを作成できる、入力が完了した後に押してもらうことでその後の処理を開始したりするのに利用できる。
B = st.button("プログラム作成")  # ボタンもラベルをつけて表示できる
# ボタンの状態を変数に代入して処理の実行や分岐に使用できる。ボタンが押されていない場合Bにはfalsが代入されている
if B:  # "計算"ボタンが押された時にBにはtrueが代入されるのでif文の処理が実行される。
    XWp = int(XW) / 2 + int(D)  # X0を設定するための座標
    YWm = int(YW) / 2 - int(YW)  # Y0を設定するための座標
    XE = int(XWp) - (int(XWp) * 3)  # Xの加工終了の位置(X-の座標)
    DP = int(D) - 20  # パスのステップ幅を計算(工具系ー20(ラップ量))
    CQ = float(Z) / float(ZP) + 1  # コピーの回数を計算
    YW = int(YW)  # フォームに入力されたY幅をintに変換
    YWa = YW + (int(D) / 2)
    Ds = int(D) / 2 - 15  # 高送りを使うと仮定しチップのR分を引いて実際に削れる幅を工具半径－15として計算、その結果を変数に代入
    YWb = YWa - 15
    YP = 0  # 次のwhile文で使う変数を先に定義しておく
    P = []  # ループ処理の結果を格納するための空のリストを作成
    proguram2 = ""

    #### 加工ピッチの計算 ####
    while YP < YW:  # YPがYWより小さい場合にtrueを返し、YWより大きくなった時にfalsを返すからそのタイミングでループ処理を抜ける。
        YP += int(DP)  # ループ処理の内容。YPとDP(加工パスのピッチ)を足し算してその結果をYPに代入(YP=YP+DPと同じ意味)
        P.append(YP)  # .append(ドットアペンド)上の処理の結果をリスト"P"に追加していく処理

    #### ここからプログラム作成開始 ####
    proguram1 = (f"G90G00X{XWp}Y{YWm}(この位置で原点X0Y0)\nM00\nVC1=0.2\nS{S}M3\nM12\nCOPY Q{int(CQ)}\nG90G00X0Y0\nZ50\nZ=VC1+5\nG01Z=VC1F{F}\n"
            f"X{XE}F{F}\nG00Z50\n")  # 原点設定する位置まで移動させて一時停止。# ここで加工開始から１回目の加工パス終了まで表示

    #### 2回目以降の加工パスのプログラム作成 ####
    for i, Yp in enumerate(P[:-1], start=1):  # リスト"P"の中身を最初から最後の１つ前まで要素とインデックスを取得して代入。
        # P[:-1]でループ処理を行う範囲を指定、:-1だとリストの要素数の最後の要素だけをスキップできる
        # enumerateはリストから要素とインデックスを同時に取得する、変数Ypに要素を代入し変数iにそのインデックスを代入。
        # オプションとしてstartを使えばインデックスの開始番号を自由に変えられる。start=1なので変数iはインデックス1から開始している
        ### for文でプログラムを繰り返し表示。最初の表示ではYpがリスト"P"の最初の要素が代入されるので2回目の加工パスの座標で表示される
        ### スライス"P[:-1]"を使ってリストの最後の要素をスキップしているので最後の１つ前の要素まで繰り返しプログラムが表示される。
        proguram2 += f"X0Y0+{Yp}\nZ=VC1+5\nG01Z=VC1F{F}\nX{XE}F{F}\nG00Z50\n"

    #### 最後の加工パスを条件で分岐させてプログラム作成 ####
    if P[-2] + Ds >= YW:  # P[-2](上のfor文で表示させた最後のYp(加工パスの座標))とDs(工具の有効半径)の合計とYW(Y幅)を比較
        proguram3 = f"VC1=VC1-{ZP}\nCOPYE\nVC1=0\nM09\nM05\nM02"  # 最後の加工パスがY幅以上(工具の幅が鋳物を削りきっている)なら表示される。
    else:  # もし上のifがfalsなら実行される処理（最後の加工パスがＹ幅以下なら実行）
        proguram3 = f"X0Y0+{YW}\nZ=VC1+5\nG01Z=VC1F{F}\nX{XE}F{F}\nG00Z50\nVC1=VC1-{ZP}\nCOPYE\nVC1=0\nM09\nM05\nM02"  # Ｙ幅と同じ座標で加工パスを追加して削りきるプログラム # VCを下げてコピーエンドと加工終了

    #### 仕上加工プログラム ####
    SXWp = int(XW) / 2 + int(DS)  # X0を設定するための座標
    SXE = int(SXWp) - (int(SXWp) * 3)  # Xの加工終了の位置(X-の座標)
    SDP = int(DS) - 20  # パスのステップ幅を計算(工具系ー20(ラップ量))
    SDs = int(DS) / 2  # 実際に削れる幅を計算、その結果を変数に代入
    SYP = 0  # 次のwhile文で使う変数を先に定義しておく
    SP = []  # ループ処理の結果を格納するための空のリストを作成
    s_proguram2 = ""

    #### 加工ピッチの計算  ####
    while SYP < YW:
        SYP += int(SDP)
        SP.append(SYP)
    #### ここからプログラム開始 ####
    s_proguram1 = f"G90G00X{SXWp}Y{YWm}(この位置で原点設定X0Y0)\nM00\nS250M3\nM12\nG90G00X0Y0\nZ50\nZ5\nG01Z-0.2F500\nX{SXE}F800\nG00Z50\n"
    #### 2回目以降の加工パスのプログラム ####
    for i, SYp in enumerate(SP[:-1], start=1):
        s_proguram2 += f"X0Y0+{SYp}\nZ5\nG01Z-0.2F500\nX{SXE}F800\nG00Z50\n"
    #### 最後の加工パスを条件で分岐させてプログラム ####
    if SP[-2] + SDs >= YW:
        s_proguram3 = "M09\nM05\nM02"
    else:
        s_proguram3 = f"X0Y0+{YW}\nZ5\nG01Z-0.2F500\nX{SXE}F800\nG00Z50\nM09\nM05\nM02"

    A_proguram_text = "\n".join([proguram1, proguram2, proguram3])
    S_proguram_text = "\n".join([s_proguram1, s_proguram2, s_proguram3])
    #### ダウンロードボタン ####
    if B:
        st.download_button(
            label=f"{filename}-ARAをダウンロード",
            data=A_proguram_text.encode("shift_jis"),
            file_name=f"{filename}-ARA.MIN",
            mime="text/plain"
        )

    if B:
        st.download_button(
            label=f"{filename}-SIAをダウンロード",
            data=S_proguram_text.encode("shift_jis"),
            file_name=f"{filename}-SIA.MIN",
            mime="text/plain"
        )

    st.text(A_proguram_text)
    st.text("\n\n\n200Φ仕上の加工プログラム\n")
    st.text(S_proguram_text)
