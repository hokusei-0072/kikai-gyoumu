import streamlit as st
import pandas as pd
from datetime import date
import re
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# =========================
# 認証情報読み込み（あなたの形式）
# =========================
google_cloud_secret = st.secrets["google_cloud"]
service_account_info = {
    "type": google_cloud_secret["type"],
    "project_id": google_cloud_secret["project_id"],
    "private_key_id": google_cloud_secret["private_key_id"],
    "private_key": google_cloud_secret["private_key"],
    "client_email": google_cloud_secret["client_email"],
    "client_id": google_cloud_secret["client_id"],
    "auth_uri": google_cloud_secret["auth_uri"],
    "token_uri": google_cloud_secret["token_uri"],
    "auth_provider_x509_cert_url": google_cloud_secret["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_cloud_secret["client_x509_cert_url"],
    "universe_domain": google_cloud_secret.get("universe_domain", "googleapis.com"),
}

SHEET_ID = st.secrets.get("sheets", {}).get(
    "SHEET_ID", "16OcFf4xMhOYb2_xCZlabO3SACkYjUFFvFN9psSxbCgw"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ✅ ここが重要：oauth2client → google.oauth2.service_account に統一
@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID).sheet1  # ← 先頭シートを返す

sheet = get_sheet()



# ====== 小ユーティリティ ======
def clean_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).replace("\u3000", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


# ====== データ読み書き ======
@st.cache_data(ttl=60)
def load_df():
    df = get_as_dataframe(sheet, evaluate_formulas=True, dtype=None, header=0)
    df = df.dropna(how="all")

    cols = ["材質", "サイズ", "仕上がり", "個数", "最終更新日"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[cols]

    df["材質"] = df["材質"].astype(str).map(clean_text)
    df["サイズ"] = df["サイズ"].astype(str).map(clean_text)
    df["仕上がり"] = pd.to_numeric(df["仕上がり"], errors="coerce").fillna(0).astype(int)
    df["個数"] = pd.to_numeric(df["個数"], errors="coerce")
    df["最終更新日"] = pd.to_datetime(df["最終更新日"], errors="coerce").dt.date
    return df


def save_df(df: pd.DataFrame):
    # 全消し→一括書き戻し（ヘッダ含む）
    sheet.clear()
    set_with_dataframe(sheet, df, include_index=False, include_column_header=True, resize=True)
    # 読み直しのためキャッシュ無効化
    st.cache_data.clear()


# ---------- アプリ本体 ----------
st.title("鋼材在庫 管理アプリ")

df = load_df()
SOUSA = st.radio("操作を選択", ["在庫の新規追加", "在庫の増減"], horizontal=True)

# 既存材質一覧（空文字除外）
maker_list = sorted(x for x in set(df["材質"].dropna()) if clean_text(x))

if SOUSA == "在庫の新規追加":
    st.subheader("在庫の新規追加")

    name_choice = st.selectbox(
        "材質を選択してください",
        ["選択してください", *maker_list, "その他材質"],
        index=0,
    )

    if name_choice == "その他材質":
        name = clean_text(st.text_input("材質を入力してください"))
    else:
        name = "" if name_choice == "選択してください" else clean_text(name_choice)

    part = clean_text(st.text_input("サイズを入力してください"))
    itaatu = st.radio("仕上がり", ["6F","4F","2F","その他"])
    maisuu = st.number_input("個数を入力してください", value=0, step=1)
    send_date = st.date_input("登録日", value=date.today())

    if name and part:
        exist = df[(df["材質"] == name) & (df["サイズ"] == part)]
        if not exist.empty:
            st.info(f"既存データあり：現在の個数 {int(exist.iloc[0]['個数'])}")

    if st.button("登録 / 反映", type="primary"):
        if not name or name == "選択してください":
            st.error("材質を選択/入力してください")
        elif not part:
            st.error("サイズを入力してください")
        else:
            mask = (df["材質"] == name) & (df["サイズ"] == part)
            if mask.any():
                df.loc[mask, ["仕上がり", "個数", "最終更新日"]] = [itaatu, int(maisuu), send_date]
            else:
                new_row = {
                    "材質": name,
                    "サイズ": part,
                    "仕上がり": itaatu,
                    "個数": int(maisuu),
                    "最終更新日": send_date,
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            save_df(df)
            st.success("保存しました！")

elif SOUSA == "在庫の増減":
    st.subheader("在庫の増減")

    maker_sel = st.selectbox(
        "材質を選択してサイズを絞り込み",
        ["選択してください", *maker_list],
        index=0,
    )

    if maker_sel == "選択してください":
        st.info("材質を選んでください。")
        st.stop()

    maker_sel = clean_text(maker_sel)
    filtered = df[df["材質"] == maker_sel].copy()

    def make_label(row):
        t = f" {row['仕上がり']}" if pd.notna(row["仕上がり"]) else ""
        return f"{row['サイズ']}{t}"

    if filtered.empty:
        st.warning("この材質に紐づく在庫がありません。")
        st.stop()

    filtered["__label__"] = filtered.apply(make_label, axis=1)

    buhin_label = st.selectbox(
        "サイズを選択してください",
        ["選択してください"] + filtered["__label__"].tolist(),
        index=0,
    )

    if buhin_label != "選択してください":
        idx_preview = filtered.index[filtered["__label__"] == buhin_label]
        if len(idx_preview) > 0:
            ridx_preview = idx_preview[0]
            cur = int(df.loc[ridx_preview, "個数"]) if pd.notna(df.loc[ridx_preview, "個数"]) else 0
            st.caption(f"現在の在庫：{cur} 個")

    change = st.number_input("増減個数（入庫ならプラス、出庫はマイナス）", value=0, step=1)
    send_date = st.date_input("更新日", value=date.today())

    if st.button("在庫を更新", type="primary"):
        if buhin_label == "選択してください":
            st.error("サイズを選択してください")
        elif change == 0:
            st.error("増減個数を入力してください（プラスまたはマイナス）")
        else:
            idx = filtered.index[filtered["__label__"] == buhin_label]
            if len(idx) == 0:
                st.error("対象データが見つかりませんでした。")
            else:
                ridx = idx[0]
                current = int(df.loc[ridx, "個数"]) if pd.notna(df.loc[ridx, "個数"]) else 0
                new_val = current + int(change)

                # 0未満を禁止する場合は以下を有効化
                # if new_val < 0:
                #     st.error("在庫がマイナスになります。値を見直してください。"); st.stop()

                df.loc[ridx, "個数"] = new_val
                df.loc[ridx, "最終更新日"] = send_date
                save_df(df)
                st.success(f"在庫を {current} → {new_val} に更新しました。")
