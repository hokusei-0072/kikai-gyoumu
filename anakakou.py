import streamlit as st

st.title("穴加工プログラム")

##### 変数定義 #####
kariteigi = [0,0,0,0]# 変数の仮定義用のリスト
TKEI = 0
toolNo = 0
RsS,RsZ,RsF,RsQ = kariteigi
TsS,TsZ,TsF,TsQ = kariteigi
RM,TM = kariteigi[:2]
RS,RZ,RF = kariteigi[:3]
TZ,TF = kariteigi[:2]

##### フォーム #####
NAIYOU = st.selectbox('加工内容',('もみつけ+リーマ','リーマ+タップ','リーマ+バカ穴','リーマ+バカ穴+その他穴あけ'))
RKEI = st.selectbox('リーマ径',('16','13','10','8','6'))
if NAIYOU == 'リーマ+タップ':
    TKEI = st.selectbox('タップ径',('M16','M12','M10','M8','M6'))
#cool = st.selectbox('クーラント',('M08','M12','M339','M50'))
if NAIYOU == 'リーマ+バカ穴+その他穴あけ':
    TOOL = st.text_input('工具番号',placeholder=15)
    ANAKEI = st.text_input('ドリル径を入力',placeholder='12.7' )
    KAITEN = st.text_input('回転数',placeholder=800)
    OKURI = st.text_input('送り',placeholder=80)
    FUKASA = st.text_input('加工深さ', placeholder=50)
    SAIKURU = st.selectbox('固定サイクルを選択',('G81','G83','G73'))
    if SAIKURU == 'G83'or SAIKURU == 'G73':
        PITCH = st.text_input('ピック量',placeholder=3)

##### リスト作成 #####
# リーマ下穴
R16s = ['(工具番号を入力)',800,200,50,5]
R13s = [4,1350,200,50,10]
R10s = [6,1000,200,45,10]
R8s = [8,1000,200,40,8]
R6s = ['(工具番号を入力)',1000,200,25,5]
# リーマ面取り
R16m = 8.3
R13m = 6.8
R10m = 5.3
R8m = 4.3
R6m = 3.3
# リーマ
R16 = ['(工具番号を入力)',250,40,30]
R13 = [5,300,40,30]
R10 = [7,350,35,30]
R8 = [9,400,30,30]
R6 = ['(工具番号を入力)',500,15,30]

# タップ下穴
T16s = [10,1000,200,55,10]
T12s = [13,1350,200,50,10]
T10s = [12,1000,200,45,10]
T8s = ['(工具番号を入力)',1000,200,40,8]
T6s = ['(工具番号を入力)',1000,200,35,5]
# タップ面取り
T16m = 8
T12m = 6
T10m = 5
T8m = 4
T6m = 3
# タップ
T16 = [45,400]
T12 = [40,350]
T10 = [35,300]
T8 = [30,250]
T6 = [25,200]

##### プログラム作成 #####
B = st.button('プログラム作成')
if B:
    st.text(f'G15H1\nG90G00G17')
    if NAIYOU == 'もみつけ+リーマ' or NAIYOU == 'リーマ+タップ' or NAIYOU == 'リーマ+バカ穴':
        st.text('G111T3\nG00X0Y0\nG56Z200HA\nS2000M3\nM08\nM53\nG71Z50\nNCYL G81Z-2R2F40\nCALL O2\n'
                'NCYL G81Z-2R2F40\nCALL O3\nG80Z500\nM09\nM5')
    elif NAIYOU == 'リーマ+バカ穴+その他穴あけ':
        st.text('G111T3\nG00X0Y0\nG56Z200HA\nS2000M3\nM08\nM53\nG71Z50\nNCYL G81Z-2R2F40\nCALL O2\n'
                'NCYL G81Z-2R2F40\nCALL O3\nNCYL G81Z-2R2F40\nCALL O4\nG80Z500\nM09\nM5')

    ##### リーマ下穴 #####
    if RKEI == '16':
        toolNo,RsS,RsF,RsZ,RsQ = R16s
    elif RKEI == '13':
        toolNo,RsS,RsF,RsZ,RsQ = R13s
    elif RKEI == '10':
        toolNo,RsS,RsF,RsZ,RsQ = R10s
    elif RKEI == '8':
        toolNo,RsS,RsF,RsZ,RsQ = R8s
    elif RKEI == '6':
        toolNo,RsS,RsF,RsZ,RsQ = R6s
    st.text(f'N20\nG111T{toolNo}\nG00X0Y0\nG56Z200HA\nS{RsS}M3\nM50\nM53\nG71Z50\n'
            f'NCYL G83Z-{RsZ}R5Q{RsQ}F{RsF}\nCALL O2\nG80Z500\nM339\nG04P10\nM09\nM05')

    ##### タップ下穴 #####
    if NAIYOU == 'リーマ+タップ':
        if TKEI == 'M16':
            toolNo,TsS,TsF,TsZ,TsQ = T16s# アンパック代入を使ってまとめて代入
            #toolNo = T16s[0],TsS = T16s[1],TsF = T16s[2],TsZ = T16s[3],TsQ = T16s[4] #普通の代入
        elif TKEI == 'M12':
            toolNo,TsS,TsF,TsZ,TsQ = T12s
        elif TKEI == 'M10':
            toolNo,TsS,TsF,TsZ,TsQ = T10s
        elif TKEI == 'M8':
            toolNo,TsS,TsF,TsZ,TsQ = T8s
        elif TKEI == 'M6':
            toolNo,TsS,TsF,TsZ,TsQ = T6s
        st.text(f'N30\nG111T{toolNo}\nG00X0Y0\nG56Z200HA\nS{TsS}M3\nM50\nM53\nG71Z50\n'
                f'NCYL G83Z-{TsZ}R5Q{TsQ}F{TsF}\nCALL O3\nG80Z500\nM339\nG04P10\nM09\nM05')
        
    ##### 面取り #####
    if NAIYOU == 'もみつけ+リーマ':
        if RKEI == '16':
            RM = R16m
        elif RKEI == '13':
            RM = R13m
        elif RKEI == '10':
            RM = R10m
        elif RKEI == '8':
            RM = R8m
        elif RKEI == '6':
            RM = R6m
        st.text(f'N30\nG111T3\nG00X0Y0\nG56Z200HA\nS2000M3\nM08\nM53\nG71Z50\n'
                f'NCYL G81Z-{RM}R5F120\nCALL O2\nG80Z500\nM09\nM05')
    elif NAIYOU == 'リーマ+タップ':
        if RKEI == '16':
            RM = R16m
        elif RKEI == '13':
            RM = R13m
        elif RKEI == '10':
            RM = R10m
        elif RKEI == '8':
            RM = R8m
        elif RKEI == '6':
            RM = R6m
    if NAIYOU == 'リーマ+タップ':
        if TKEI == 'M16':
                TM = T16m
        elif TKEI == 'M12':
            TM = T12m
        elif TKEI == 'M10':
            TM = T10m
        elif TKEI == 'M8':
            TM = T8m
        elif TKEI == 'M6':
            TM = T6m
        st.text(f'N40\nG111T3\nG00X0Y0\nG56Z200HA\nS2000M3\nM08\nM53\nG71Z50\n'
                f'NCYL G81Z-{RM}R5F120\nCALL O2\nNCYL G81Z-{TM}R5F120\nCALL O3\nG80Z500\nM09\nM05')

    ##### リーマ #####
    if RKEI == '16':
        toolNo,RS,RZ,RF = R16
    elif RKEI == '13':
        toolNo,RS,RZ,RF = R13
    elif RKEI == '10':
        toolNo, RS, RZ, RF = R10
    elif RKEI == '8':
        toolNo, RS, RZ, RF = R8
    elif RKEI == '6':
        toolNo,RS, RZ, RF = R6
    if NAIYOU == 'もみつけ+リーマ':
        st.text(f'N40\nG111T{toolNo}\nY500\nM00\nG00X0Y0\nG56Z200HA\nS{RS}M3\nM50\nM53\nG71Z50\n'
                f'NCYL G81Z-{RZ}R5F{RF}\nCALL O2\nG80Z500\nM339\nG04P10\nM09\nM05')
    elif NAIYOU == 'リーマ+タップ':
        st.text(f'N50\nG111T{toolNo}\nY500\nM00\nG00X0Y0\nG56Z200HA\nS{RS}M3\nM50\nM53\nG71Z50\n'
                f'NCYL G81Z-{RZ}R5F{RF}\nCALL O2\nG80Z500\nM339\nG04P10\nM09\nM05')

 ##### タップ #####
    if TKEI == 'M16':
        TZ,TF = T16
    elif TKEI == 'M12':
        TZ,TF = T12
    elif TKEI == 'M10':
        TZ,TF = T10
    elif TKEI == 'M8':
        TZ,TF = T8
    elif TKEI == 'M6':
        TZ,TF = T6
    if NAIYOU == 'リーマ+タップ':
        st.text(f'N60\nG111T25\nY500\nM00\nG00X0Y0\nG56Z200HA\nS200M3\nM08\nM53\nG71Z50\n'
                f'NCYL G84Z-{TZ}R10F{TF}\nCALL O3\nG80Z500\nM09\nM05')
    st.text('N99\nM01\nG00Z500\nX-500Y-500\nM02')
    st.text('O2(リーマの座標を貼り付け)\nRTS')
    if NAIYOU == 'もみつけ+リーマ':
        st.text('O3(もみつけの座標を貼り付け)\nRTS)')
    elif NAIYOU == 'リーマ+タップ':
        st.text('O3(タップの座標を貼り付け)\nRTS)')



